from datetime import datetime
import json
import time

import pandas as pd
from sortedcontainers import SortedList

from .mixins import MetricProcessor, BacktestStrategyInitializer


# def get_dataset_data(filename):
#     # Загружаем данные из CSV файла
#     data = pd.read_csv(filename, names=["Date", "Time", "Open", "High", "Low", "Close", "Volume"])

#     # Добавляем столбец с datetime
#     data['Datetime'] = pd.to_datetime(data['Date'] + ' ' + data['Time'])
#     data.set_index('Datetime', inplace=True)
#     data.drop(['Date', 'Time'], axis=1, inplace=True)
#     return data


class BacktestStrategyProcessor(BacktestStrategyInitializer, MetricProcessor):

    def __init__(self, data, strategy, trend_type, point, spread, is_multiprocessing=False):
        self.strategy = strategy
        self.data = data
        self.closed_trades = []
        self.signal_step = 0
        self.open_trades = {}
        self.point = point
        self.spread = spread
        self.initial_capital = 100000  # начальный капитал
        self.trend_type = trend_type
        self.is_multiprocessing = is_multiprocessing
        self.with_ai = False

    def set_with_ai(self, prediction_service):
        self.with_ai = True
        self.prediction_service = prediction_service

    def _dataframe_generator(self, df):
        for index, row in df.iterrows():
            yield index, row

    def handle_trade_opening(self, index, row, current_date, previous_candles, sl_open_trades, tp_open_trades):
        if self.signal_step + 1 != len(self.entry_deal[self.trend_type]):
            self.signal_step += 1
            return
        open_price = self.get_current_price(row['Close'])
        sl_price, tp_price = self.get_trade_limits(open_price, previous_candles)
        tp_result = round((tp_price - open_price) / self.point * self.lot, 2) if self.trend_type == "buy" else round((open_price - tp_price) / self.point * self.lot, 2)
        sl_result = round((sl_price - open_price) / self.point * self.lot, 2) if self.trend_type == "buy" else round((open_price - sl_price) / self.point * self.lot, 2)

        self.open_trades[str(index)] = {
            'open_index': current_date,
            'open_price': open_price,
            'trend_type': self.trend_type,
            'sl_price': sl_price,
            'tp_price': tp_price,
            'open_time': current_date,
            'tp_result': tp_result,
            'sl_result': sl_result,
        }

        sl_open_trades.add((sl_price, str(index)))
        tp_open_trades.add((tp_price, str(index)))
        self.signal_step = 0

    def process_strategy(self):
        start_time = time.time()
        self._startegy_converter(self.strategy)
        sl_open_trades = SortedList(key=lambda x: -x[0]) if self.trend_type == "buy" else SortedList()
        tp_open_trades = SortedList() if self.trend_type == "buy" else SortedList(key=lambda x: -x[0])
        previous_candles = []
        for index, row in self._dataframe_generator(self.data):
            previous_candles.append(row)
            if len(previous_candles) > 50:
                previous_candles = previous_candles[1:]
            else:
                continue
            # Условия для открытия сделки
            current_condition = self.entry_deal[self.trend_type][self.signal_step]
            current_date = datetime.strptime(str(index), "%Y-%m-%d %H:%M:%S")
            is_confirmed = True
            for sub_condition in current_condition:
                left = self.get_condition_value(sub_condition['left_condition'], row, previous_candles)
                right = self.get_condition_value(sub_condition['right_condition'], row, previous_candles)
                is_confirmed = self.check_condition(left, right, sub_condition['conditions_delimiter'])
                if not is_confirmed:
                    break
            if is_confirmed:
                self.handle_trade_opening(index, row, current_date, previous_candles, sl_open_trades, tp_open_trades)

            # Проверяем открытые сделки на стоп-лосс или тейк-профит
            for i in range(len(sl_open_trades) -1, 0, -1):
                val = sl_open_trades[i][0]
                open_index = sl_open_trades[i][1]
                if not self.open_trades.get(open_index):
                    del sl_open_trades[i]
                    continue
                if (val > row['Low'] and self.trend_type == "buy") or (val < row['High'] and self.trend_type == "sell"):
                    break
                trade = {
                    **self.open_trades[open_index],
                }
                trade['close_index'] = current_date
                trade['close_price'] = trade['sl_price']
                trade['close_time'] = current_date
                trade['result'] = 'SL'
                trade['profit'] = trade['sl_result']
                if self.with_ai:
                    data4predict = self.prediction_service.get_predict_data([x.values for x in previous_candles])
                    trade['data4predict'] = data4predict
                self.closed_trades.append(trade)
                del self.open_trades[open_index]
                del sl_open_trades[i]

            for i in range(len(tp_open_trades) -1, 0, -1):
                val = tp_open_trades[i][0]
                open_index = tp_open_trades[i][1]
                if not self.open_trades.get(open_index):
                    del tp_open_trades[i]
                    continue
                if (val < row['High'] and self.trend_type == "buy") or (val > row['Low'] and self.trend_type == "sell"):
                    break
                trade = self.open_trades[open_index]
                trade['close_index'] = current_date
                trade['close_price'] = trade['tp_price']
                trade['close_time'] = current_date
                trade['result'] = 'TP'
                trade['profit'] = trade['tp_result']
                print(trade['result'], trade['profit'])
                if self.with_ai:
                    data4predict = self.prediction_service.get_predict_data([x.values for x in previous_candles])
                    trade['data4predict'] = data4predict
                self.closed_trades.append(trade)
                del self.open_trades[open_index]
                del tp_open_trades[i]
        del sl_open_trades
        del tp_open_trades
        del previous_candles
        if self.with_ai and len(self.closed_trades) > 0:
            predictions = []
            batch_size = 10000
            batches_count = len(self.closed_trades) // batch_size
            if len(self.closed_trades) % batch_size > 0:
                batches_count += 1
            for batch_step in range(batches_count):
                current_data4predict = [x['data4predict'] for x in self.closed_trades[batch_step*batch_size:(batch_step + 1)*batch_size]]
                batch_predictions, error = self.prediction_service.predict_batch(current_data4predict, self.trend_type)
                if not batch_predictions:
                    raise Exception(f"Prediction Error: {error}")
                
                predictions += batch_predictions['predictions']
            self.closed_trades = [self.closed_trades[i] for i, val in enumerate(predictions) if val['prediction'] is True]
        metrics = self.calculate_main_metrics()
        additional_metrics = self.calculate_additional_metrics()
        metrics['additional_metrics'] = additional_metrics
        end_time = time.time() -start_time
        print(end_time)
        return metrics

    def get_condition_value(self, condition, candles_data, previous_candles):
        result = None
        if condition['group'] == "value":
            mp = {x['name']:x['value'] for x in condition['main_parametres']}
            result = float(mp['Value'])
            if mp['In pips']:
                result = result * self.point
        if condition['group'] == "indicators":
            column_name = condition["column_name"]
            result = candles_data[column_name]
        if condition['group'] == "candlestick_pattern":
            pattern_name = condition['main_parametres'][0]['value']
            pattern_value = candles_data[pattern_name] / 100
            check_value = condition['add_parametres'][0]['value']
            check_value = 1 if "Grow" else -1
            result = pattern_value == check_value
        if condition['group'] == "price":
            result = candles_data['Close']
            price_type = condition['main_parametres'][0]['value']
            if price_type == "Ask":
                result += self.spread
        if condition['group'] == "pattern":
            pattern_name = condition['main_parametres'][0]['value']
            ap_map = {x['name']: x['value'] for x  in condition['add_parametres']}
            window = ap_map["Window"]
            value = str(candles_data[f"{pattern_name}_{window}"])
            check_value = ap_map['Type']
            result = value == check_value
        if condition['group'] == "candlestick":
            parametres = {x['name']: x['value'] for x  in condition['main_parametres']}
            candle_index = parametres['Candlestick Index']
            value_type = parametres["Candlestick Value"]
            candle = previous_candles[len(previous_candles) - 1 - candle_index]
            is_candle_bull = candle["Close"] > candle["Open"]

            value_map = {
                "Open": candle["Open"],
                "High": candle["High"],
                "Low": candle["Low"],
                "Close": candle["Close"],
                "Range": candle["High"] - candle["Low"],
                "Body length": candle["Close"] - candle["Open"] if is_candle_bull else candle["Open"] - candle["Close"],
                "Upper wick": candle["High"] - candle["Close"] if is_candle_bull else candle["High"] - candle["Open"],
                "Lower wick": candle["Open"] - candle["Low"] if is_candle_bull else candle["Close"] - candle["Low"]
            }
            result = value_map.get(value_type, 0)
        return result

    def get_trade_limits(self, open_price, previos_candles):
        self.exit_deal['take-profit-type'] = "relative"
        self.exit_deal['take-profit-value'] = 4
        sl_type = self.exit_deal['stop-loss-type']
        if sl_type == "fixed":
            sl_points = int(self.exit_deal['stop-loss-value'])
            if self.trend_type == "buy":
                sl_price = open_price - sl_points * self.point  # Рассчитываем цену стоп-лосса
            else:
                sl_price = open_price + (sl_points * self.point)  # Рассчитываем цену стоп-лосса
        if sl_type == "dynamic":
            candles_count = int(self.exit_deal['stop-loss-value'])
            if self.trend_type == "buy":
                sl_price = min([
                    x['Low'] for x in previos_candles[len(previos_candles) - 1 -candles_count:]
                ])
            else:
                sl_price = max([
                    x['High'] for x in previos_candles[len(previos_candles) - 1 -candles_count:]
                ])
        tp_type = self.exit_deal['take-profit-type']
        if tp_type == "fixed":
            tp_points = int(self.exit_deal['take-profit-value'])
            if self.trend_type == "buy":
                tp_price = open_price + tp_points * self.point  # Рассчитываем цену тейк-профита
            else:
                tp_price = open_price - tp_points * self.point  # Рассчитываем цену тейк профита
        if tp_type == "dynamic":
            candles_count = int(self.exit_deal['take-profit-value'])
            if self.trend_type == "buy":
                tp_price = max([
                    x['High'] for x in previos_candles[len(previos_candles) - 1 -candles_count:]
                ])
            else:
                tp_price = min([
                    x['Low'] for x in previos_candles[len(previos_candles) - 1 -candles_count:]
                ])
        if tp_type == "relative":
            multiply_value = int(self.exit_deal['take-profit-value'])
            if self.trend_type == "buy":
                base_points = (open_price - sl_price) / self.point
                tp_points = base_points * multiply_value
                tp_price = open_price + tp_points * self.point
            else:
                base_points = (sl_price - open_price) / self.point
                tp_points = base_points * multiply_value
                tp_price = open_price - tp_points * self.point  # Рассчитываем цену тейк профита
        return sl_price, tp_price

    def get_current_price(self, price_value):
        if self.trend_type == "buy":
            return price_value - self.spread * self.point
        return price_value + self.spread * self.point


    def check_condition(self, left, right, delimiter):
        if left is None or right is None:
            return False
        comparator_map = {
            "<": left < right,
            ">": left > right,
            "=": left == right,
            "!=": left != right,
            ">=": left >= right,
            "<=": left <= right
        }
        result = comparator_map.get(delimiter, False)
        return result


# if __name__ == "__main__":
#     main_strat_time = time.time()
#     filename = "../scripts/quotes/EURUSD_60_2016-01-01_2024-06-01.csv"
#     data = get_dataset_data(filename)
#     strategy_config_filename = "strategies/Triangles.json"
#     with open(strategy_config_filename, "r") as json_file:
#         strategy_config = json.load(json_file)
#     trend_types = ["buy", "sell"]
#     for trend_type in trend_types:
#         StrategyTester = BacktestStrategyProcessor(data, strategy_config, trend_type)
#         StrategyTester.process_strategy()
#         additional_metrics = StrategyTester.calculate_additional_metrics()
#         main_metrics = StrategyTester.calculate_main_metrics()

#         full_metrics = {
#             **main_metrics,
#             **additional_metrics,
#         }

#         with open(f"report_{trend_type}.json", "w") as json_file:
#             json.dump(full_metrics, json_file, indent=3, ensure_ascii=False)

#         analyze_textv2 = StrategyTester.analyze_trading_reportv2(full_metrics)
#         with open(f"human_report2_{trend_type}.txt", "w") as txt_file:
#             txt_file.write(analyze_textv2)

#     main_end_time = time.time() - main_strat_time
#     print("Время всего анализа:", main_end_time)