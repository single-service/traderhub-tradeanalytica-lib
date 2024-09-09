import json
from unittest import TestCase

import pandas as pd

from traderhub_tradeanalytica import ConditionChecker, BacktestStrategyProcessor


class ConditionCheckerTest(TestCase):

    def setUp(self):
        parametres_file_path = f"test_data/full_parametres_combinations.json"
        self.parameters = []
        with open(parametres_file_path, "r") as json_file:
            self.parameters = json.load(json_file)
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
        candles = candles.iloc[:50]
        self.candles = candles
        self.current_candle = candles.iloc[49]
        self.point = 0.0001
        spread = 15 * self.point
        self.ask_price = self.current_candle['Open'] + spread
        self.bid_price = self.current_candle['Open']

    def test_conditions(self):
        checker = ConditionChecker(
            self.current_candle,
            self.candles,
            self.ask_price,
            self.bid_price,
            self.point
        )
        for config in self.parameters:
            result = checker.get_condition_value(config)
            self.assertIsNotNone(result, f"Вернулся None, config: {config}")
        print("Готово")


class BacktestTest(TestCase):
    def setUp(self):
        strategy_file_path = f"test_data/strategy.json"
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
