import inspect

import pandas_ta as ta
import talib

from ..references.indicators_models.indicators_talib_map import get_indicators_talib_data, get_prefix, find_indicator_column
from ..executors.patternpy.functions_map import TRADEPATTERNS_MAP


class BacktestStrategyInitializer:
    def _startegy_converter(self, strategy):
        self.lot = strategy.get("lot")
        self.exit_deal = strategy.get("exit-deal")
        self.entry_deal = strategy.get("entry-deal")
        self._collect_indicators()
        if self.indicators_map:
            self._convert_data_by_indicators_map()
            columns = self.data.columns.to_list()
            steps = self.entry_deal[self.trend_type]
            for i, step in enumerate(steps):
                for ii, condition in enumerate(step):
                    sides = ['left', 'right']
                    for side in sides:
                        condition_side = condition[f"{side}_condition"]
                        if condition_side['group'] in ("price", "candlestick", "value"):
                            continue
                        if condition_side['group'] == "indicators":
                            column_name = find_indicator_column(columns, condition_side)
                            if column_name is None:
                                print(f"Ошибка обработки: column not finded: {condition_side}")
                                continue
                            self.entry_deal[self.trend_type][i][ii][f"{side}_condition"]["column_name"] = column_name
        self._collect_pattern_columns()
        if self.candlestick_pattern_columns:
            for pattern_name in self.candlestick_pattern_columns:
                func = getattr(talib, pattern_name, None)
                values = func(self.data['Open'], self.data['High'], self.data['Low'], self.data['Close'])
                self.data[pattern_name] = values
        if self.pattern_map:
            for column_name, params in self.pattern_map.items():
                pattern_name = params[0]
                func = TRADEPATTERNS_MAP[pattern_name]["func"]
                pattern_data = func(self.data, params[1])
                self.data[column_name] = pattern_data[TRADEPATTERNS_MAP[pattern_name]["result_column"]]
                del pattern_data
        print("startegy_converter success")
        
    def _convert_data_by_indicators_map(self):
        indicators_without_stoch = [v for _, v in self.indicators_map.items() if v['kind'] != "stoch"]
        if indicators_without_stoch:
            CustomStrategy = ta.Strategy(
                name="My strategy",
                description="Strategy description",
                ta=indicators_without_stoch
            )
            if not self.is_multiprocessing:
                self.data.ta.cores = 0
            self.data.ta.strategy(CustomStrategy, mp_context="forkserver")
        stoch_indicators = [v for _, v in self.indicators_map.items() if v['kind'] == "stoch"]
        for indicator in stoch_indicators:
            slowk, slowd = talib.STOCH(self.data['High'], self.data['Low'], self.data['Close'], fastk_period=indicator['k'], slowk_period=indicator['smooth_k'], slowd_period=indicator['d']) 
            self.data[f"{indicator['prefix']}_STOCHk_"] = slowk
            self.data[f"{indicator['prefix']}_STOCHd_"] = slowd
            del slowk
            del slowd

    def _collect_indicators(self):
        indicators_map = {}
        sides = ["left", "right"]
        for step in self.entry_deal[self.trend_type]:
            for condition in step:
                for side in sides:
                    condition_side = condition[f"{side}_condition"]
                    if condition_side['group'] != "indicators":
                        continue
                    indicator_name = condition_side['main_parametres'][0]['value']
                    key, indicator_data = get_indicators_talib_data(indicator_name, condition_side['add_parametres'])
                    if key not in indicators_map:
                        indicators_map[key] = indicator_data
        self.indicators_map = indicators_map

    def _collect_pattern_columns(self):
        candlestick_pattern_columns = set()
        pattern_map = {}
        sides = ["left", "right"]
        for step in self.entry_deal[self.trend_type]:
            for condition in step:
                for side in sides:
                    condition_side = condition[f"{side}_condition"]
                    if condition_side['group'] not in ("candlestick_pattern", "pattern",):
                        continue
                    if condition_side['group'] == "candlestick_pattern":
                        pattern_name = condition_side['main_parametres'][0]['value']
                        candlestick_pattern_columns.add(pattern_name)
                    if condition_side['group'] == "pattern":
                        pattern_name = condition_side['main_parametres'][0]['value']
                        ap_map = {x['name']: x['value'] for x in condition_side['add_parametres']}
                        window = ap_map['Window']
                        pattern_map[f"{pattern_name}_{window}"] = (pattern_name, window,)
        self.candlestick_pattern_columns = candlestick_pattern_columns
        self.pattern_map = pattern_map