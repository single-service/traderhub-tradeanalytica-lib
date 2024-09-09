import json
from unittest import TestCase

import pandas as pd

from traderhub_tradeanalytica import ConditionChecker, BacktestStrategyProcessor


class BacktestTest(TestCase):
    def setUp(self):
        strategy_file_path = f"test_data/3EMA.json"
        with open(strategy_file_path, "r") as json_file:
            self.strategy = json.load(json_file)
        candles_path = f"test_data/EURUSD_60_2016-01-01_2024-06-01.csv"
        candles = pd.read_csv(
            candles_path,
            names=['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume'],
            index_col=False
        )
        # Создание новой колонки 'Datetime' путем объединения 'Date' и 'Time'
        candles['Datetime'] = pd.to_datetime(candles['Date'] + ' ' + candles['Time'], format='%Y.%m.%d %H:%M')

        # Удаление исходных колонок 'Date' и 'Time'
        candles.drop(columns=['Date', 'Time'], inplace=True)

        # Удаление дубликатов по индексу
        candles = candles[~candles.index.duplicated(keep='first')]

        # Установка колонки 'Datetime' в качестве индекса
        candles.set_index('Datetime', inplace=True)
        self.candles = candles

    def test_backtest(self):
        point = 0.0001
        spread = 15 * point
        trade_types = ["sell", "buy"]
        for trade_type in trade_types:
            backtest_service = BacktestStrategyProcessor(self.candles, self.strategy, trade_type, point, spread)
            backtest_service.process_strategy()
            main_metrics = backtest_service.calculate_main_metrics()
            additional_metrics = backtest_service.calculate_additional_metrics()
            main_metrics['additional_metrics'] = additional_metrics
            if additional_metrics is None:
                return
            report_params = {
                **main_metrics,
                **additional_metrics
            }
            report = backtest_service.analyze_trading_report(report_params)
            report2 = backtest_service.analyze_trading_reportv2(report_params)
            print(main_metrics)