import os
import json
from unittest import TestCase

import requests
import pandas as pd
import talib
import numpy as np

from traderhub_tradeanalytica import BacktestStrategyProcessor


class PredictionService:

    def __init__(self, prediction_url=None, token=None):
        self.prediction_url = prediction_url if prediction_url else os.getenv("PREDICTION_SERVICE_HOST")
        self.service_token = token if token else os.getenv("PREDICTION_SERVICE_TOKEN")

    def _flatten_sum(self, matrix):
        return sum(matrix, [])

    def get_predict_data(self, candles):
        open = np.array([candle[0] for candle in candles], dtype=float)
        high = np.array([candle[1] for candle in candles], dtype=float)
        low = np.array([candle[2] for candle in candles], dtype=float)
        close = np.array([candle[3] for candle in candles], dtype=float)
        volume = np.array([candle[4] for candle in candles], dtype=float)
        result = []
        ma_9 = talib.EMA(close, timeperiod=9)
        ma_14 = talib.EMA(close, timeperiod=14)
        ma_21 = talib.EMA(close, timeperiod=21)
        macd, macd_signal, _ = talib.MACD(
            close,
            fastperiod=12,
            slowperiod=26,
            signalperiod=9
        )
        obv = talib.OBV(close, volume)
        slowk, slowd = talib.STOCH(
            high,
            low,
            close,
            fastk_period=5,
            slowk_period=3,
            slowk_matype=1,
            slowd_period=3,
            slowd_matype=1
        )

        result = [
            [
                open[i], high[i], low[i], close[i], volume[i],
                ma_9[i], ma_14[i], ma_21[i],
                macd[i], macd_signal[i],
                obv[i], slowk[i], slowd[i]
            ]
            for i in range(40, 50)
        ]
        result = self._flatten_sum(result)
        return result

    def get_prediction_row(self, trend, candles, operation_date, price):
        candles_data = self._get_predict_data(candles.values.tolist())
        return candles_data

    def predict(self, prediction_row):
        payload = {
            "predict_string": prediction_row
        }
        endpoint_url = f"{self.prediction_url}/predict/predict/"
        headers = {
            "X-Service-Token": self.service_token
        }
        response = requests.post(endpoint_url, json=payload, headers=headers)
        if response.status_code != 200:
            return None, f"Request Error: status_code: {response.status_code}; error: {response.text}"
        data = response.json()
        return data, None

    def predict_batch(self, prediction_data, trend_type):
        payload = {
            "predict_strings": prediction_data,
            "trend_type": trend_type
        }
        endpoint_url = f"{self.prediction_url}/predict/predict_batch/"
        headers = {
            "X-Service-Token": self.service_token
        }
        response = requests.post(endpoint_url, json=payload, headers=headers)
        if response.status_code != 200:
            return None, f"Request Error: status_code: {response.status_code}; error: {response.text}"
        data = response.json()
        return data, None



class BacktestPredictionTest(TestCase):
    def setUp(self):
        strategy_file_path = f"test_data/stohastic_trategy.json"
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

    def test_prediction_backtest(self):
        point = 0.0001
        spread = 15 * point
        trade_types = ["sell", "buy"]
        for trade_type in trade_types:
            if trade_type == "sell":
                continue
            backtest_service = BacktestStrategyProcessor(self.candles, self.strategy, trade_type, point, spread)
            prediction_host = ""
            prediction_token = ""
            prediction_service = PredictionService(prediction_host, prediction_token)
            backtest_service.set_with_ai(prediction_service)
            metrics = backtest_service.process_strategy()
            print(metrics)
