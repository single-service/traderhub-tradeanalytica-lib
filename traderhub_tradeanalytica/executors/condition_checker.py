import pandas_ta as ta
import talib

from .patternpy.functions_map import TRADEPATTERNS_MAP
from .checker_mixins import IndicatorCheckerMixin


class ConditionChecker(IndicatorCheckerMixin):

    def __init__(self, current_candle, candles, ask, bid, point):
        self.current_candle = current_candle
        self.candles = candles
        self.ask = ask
        self.bid = bid
        self.point = point

    def get_from_value(self, parametres):
        value = float(parametres['Value'])
        result = value * self.point if parametres['In pips'] else value
        return result

    def get_from_price(self, parametres):
        price = self.ask if parametres['Price'] == "Ask" else self.bid
        return price

    def get_from_candlestick(self, parametres):
        candle_index = parametres['Candlestick Index']
        value_type = parametres["Candlestick Value"]
        candle = self.current_candle if candle_index == 0 else self.candles.iloc[candle_index * -1]
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

    def get_from_indicators(self, main_parametres, ap):
        # Проверка и удаление дубликатов индексов
        if not self.candles.index.is_unique:
            self.candles = self.candles[~self.candles.index.duplicated(keep='first')]

        if not ap:
            ap = {}
        indicator_name = main_parametres['Indicator']
        shift = ap.get("Shift")
        ma_method = ap.get("MA Method")
        ma_map = {
            "Simple": "sma",
            "Exponential": "ema",
            "Smoothed": "wma"
        }
        if ma_method:
            ma_method = ma_map.get(ma_method)

        indicator_map = {
            "Awesome Oscillator": lambda: ta.ao(self.candles['High'], self.candles['Low'], fast=ap['Fast'], slow=ap['Slow'], offset=shift),  # noqa
            "Average True Range": lambda: ta.atr(self.candles['High'], self.candles['Low'], self.candles['Close'], length=ap['Period']),  # noqa
            "Even Better Sinewave": lambda: ta.ebsw(self.candles['Close'], length=ap['Period'], bars=ap['Bars'], offset=shift),  # noqa
            "MACD": lambda: self.get_macd(main_parametres, ap, shift),
            "Momentum": lambda: ta.mom(self.candles[ap['Apply To']], length=ap['Period'], offset=shift),  # noqa
            "Money Flow Index": lambda: ta.mfi(self.candles['High'], self.candles['Low'], self.candles['Close'], self.candles['Volume'], length=ap['Period'], offset=shift),  # noqa
            "Moving Average": lambda: self.get_moving_average(ap, shift),
            "On Balance Volume": lambda: ta.obv(self.candles[ap['Apply To']], self.candles['Volume'], offset=shift),  # noqa
            "Stohastic Oscillator": lambda: self.get_stochastic_oscillator(ap, shift),
            "Absolute Price Oscillator": lambda: ta.apo(self.candles['Close'], fast=ap['Fast'], slow=ap['Slow'], mamode=ma_method, offset=shift),  # noqa
            "Relative Strength Index (RSI)": lambda: ta.rsi(self.candles['Close'], length=ap['Period'], scalar=ap['Scalar'], offset=shift),  # noqa
            "Commodity Channel Index (CCI)": lambda: ta.cci(self.candles['High'], self.candles['Low'], self.candles['Close'], length=ap['Period'], c=ap['Period'],  offset=shift),  # noqa
            "Fisher Transform": lambda: ta.fisher(self.candles['High'], self.candles['Low'], length=ap['Period'], signal=ap['Signal Period'], offset=shift),  # noqa
            "Relative Vigor Index (RVGI)": lambda: ta.rvgi(self.candles['Open'], self.candles['High'], self.candles['Low'], self.candles['Close'], length=ap['Period'], swma_length=ap['SWMA Period'], offset=shift),  # noqa
            "True Strength Index (TSI)": lambda: self.get_tsi(ap, shift, ma_method),
            "Aberration": lambda: self.get_abberation(ap, shift),
            "Mass Index": lambda: ta.massi(self.candles['High'], self.candles['Low'], fast=ap['Fast'], slow=ap['Slow'], offset=shift),  # noqa
            "Donchian Channel": lambda: self.get_donchain(ap, shift),
            "Keltner Channel": lambda: self.get_keltner(ap, shift, ma_method),
            "Average Directional Index (ADX)": lambda: self.get_adx(ap, shift, ma_method),
            "Vertical Horizontal Filter": lambda: ta.vhf(self.candles['Close'], length=ap['Period'], offset=shift),  # noqa
            "Vortex": lambda: self.get_vortex(ap, shift),
            "Aroon": lambda: self.get_aroon(ap, shift),
            "Accumulation/Distribution Index": lambda: ta.ad(self.candles['High'], self.candles['Low'], self.candles['Close'], self.candles['Volume'], self.candles['Open'], offset=shift),  # noqa
            "Chaikin Money Flow": lambda: ta.cmf(self.candles['High'], self.candles['Low'], self.candles['Close'], self.candles['Volume'], self.candles['Open'], length=ap['Period'], offset=0),  # noqa
            "Fibonacci's Weighted Moving Average": lambda: ta.fwma(self.candles['Close'], length=ap['Period'], asc=ap['ASC'], offset=shift),  # noqa
            "Gann High-Low Activator": lambda: self.get_gann(ap, shift, ma_method),
        }

        func = indicator_map.get(indicator_name, lambda: 0)
        indicator_values = func()
        result = indicator_values.iloc[-1] if len(indicator_values) > 0 else 0
        return result

    def get_from_candlestick_pattern(self, main_parametres, add_parametres):
        pattern_name = main_parametres['Pattern']
        func = getattr(talib, pattern_name, None)
        if not func:
            return None
        values = func(self.candles['Open'], self.candles['High'], self.candles['Low'], self.candles['Close'])
        if len(values) == 0:
            return None
        pattern_type = add_parametres['Type']
        check_value = 100 if pattern_type == "Grow" else -100
        result = values.iloc[-1] == check_value
        return result

    def get_from_pattern_detector(self, main_parametres, add_parametres):
        pattern_name = main_parametres['Pattern']
        window = add_parametres.get("Window", 5)
        func = TRADEPATTERNS_MAP.get(pattern_name)
        if not func:
            return None
        results = func['func'](self.candles, window=window)
        if results is None:
            return None
        result = str(results.iloc[-1].get(func['result_column'], 'nan'))
        return result == add_parametres.get("Type")

    def get_condition_value(self, condition):
        value = None
        group = condition['group']
        main_parametres = {x['name']: x['value'] for x in condition['main_parametres']}
        add_parametres = {x['name']: x['value'] for x in condition['add_parametres']}

        method_map = {
            "indicators": self.get_from_indicators,
            "value": self.get_from_value,
            "candlestick": self.get_from_candlestick,
            "price": self.get_from_price,
            "candlestick_pattern": self.get_from_candlestick_pattern,
            "pattern": self.get_from_pattern_detector
        }
        method = method_map.get(group)
        if method:
            value = method(main_parametres, add_parametres) if group not in ("value", "price", "candlestick",) else method(main_parametres)  # noqa
        return value

    def check_condition(self, condition):
        left = self.get_condition_value(condition['left_condition'])
        right = self.get_condition_value(condition['right_condition'])
        if left is None or right is None:
            return False
        delimiter = condition['conditions_delimiter']
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

    def check_step(self, step_conditions):
        for condition in step_conditions:
            if not self.check_condition(condition):
                return False
        return True
