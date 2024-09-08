import pandas_ta as ta


class IndicatorCheckerMixin:

    def _get_indicator_values(self, chosen_column, choises, data):
        header_name = data.columns[choises.index(chosen_column)]
        values = data[header_name]
        return values

    def get_macd(self, main_parametres, add_parametres, shift):
        fast_value = add_parametres['Fast EMA']
        slow_value = add_parametres['Slow EMA']
        signal_value = add_parametres['MACD SMA']
        data = ta.macd(
            self.candles[add_parametres['Apply To']],
            fast=fast_value,
            slow=slow_value,
            signal=signal_value,
            offset=shift
        )
        values = data[f'MACD_{fast_value}_{slow_value}_{signal_value}']
        if add_parametres["Indicator Buffer"] == "Signal line":
            values = data[f'MACDs_{fast_value}_{slow_value}_{signal_value}']
        return values

    def get_moving_average(self, add_parametres, shift):
        ma_method = add_parametres['MA Method']
        ma_function = {
            "Simple": ta.sma,
            "Exponential": ta.ema,
            "Smoothed": ta.wma
        }.get(ma_method)
        result = ma_function(self.candles[add_parametres['Apply To']], length=add_parametres['Period'], offset=shift)
        return result

    def get_stochastic_oscillator(self, add_parametres, shift):
        ma_types = {
            "Simple": "sma",
            "Exponential": "ema",
            "Smoothed": "wma"
        }
        k_value = add_parametres["%K Period"]
        slow_value = add_parametres["Slowing"]
        d_value = add_parametres["%D Period"]
        ma_type = ma_types[add_parametres['MA Method']]
        data = ta.stoch(
            self.candles['High'],
            self.candles['Low'],
            self.candles['Close'],
            k=k_value,
            smooth_k=slow_value,
            mamode=ma_type,
            d=d_value,
            offset=shift
        )
        identifier_column = "STOCHk" if add_parametres["Indicator Buffer"] == "Base line" else "STOCHd"

        column_name = [x for x in data.columns if x.split("_")[0] == identifier_column]
        if not column_name:
            return None
        values = data[column_name[0]]
        return values

    def get_abberation(self, add_parametres, shift):
        data = ta.aberration(
            self.candles['High'],
            self.candles['Low'],
            self.candles['Close'],
            length=add_parametres['Period'],
            atr_length=add_parametres['ATR Period'],
            offset=shift
        )
        abb_type = add_parametres['ATR Type']
        values = data[f'ABER_{abb_type.upper()}_{add_parametres["Period"]}_{add_parametres["ATR Period"]}']
        return values

    def get_tsi(self, add_parametres, shift, matype):
        data = ta.tsi(
            self.candles['Close'],
            fast=add_parametres['Fast'],
            slow=add_parametres['Slow'],
            signal=add_parametres['Signal Period'],
            scalar=add_parametres['Scalar'],
            mamode=matype,
            offset=shift,
        )
        indicator_type = add_parametres['Indicator Type']
        indicator_header = f"TSI_{add_parametres['Fast']}_{add_parametres['Slow']}_{add_parametres['Signal Period']}"
        if indicator_type == "Signal line":
            indicator_header = f"TSIs_{add_parametres['Fast']}_{add_parametres['Slow']}_{add_parametres['Signal Period']}"  # noqa
        values = data[indicator_header]
        return values

    def get_donchain(self, add_parametres, shift):
        data = ta.donchian(
            self.candles['High'],
            self.candles['Low'],
            lower_length=add_parametres['Low Period'],
            upper_length=add_parametres['Up Period'],
            offset=shift
        )
        donchain_type = add_parametres['Donchian Type']
        # DCL_20_20  DCM_20_20  DCU_20_20
        indicator_header = f"DCL_{add_parametres['Low Period']}_{add_parametres['Up Period']}"
        if donchain_type == "mid":
            indicator_header = f"DCM_{add_parametres['Low Period']}_{add_parametres['Up Period']}"
        if donchain_type == "upper":
            indicator_header = f"DCU_{add_parametres['Low Period']}_{add_parametres['Up Period']}"
        values = data[indicator_header]
        return values

    def get_keltner(self, add_parametres, shift, matype):
        data = ta.kc(
            self.candles['High'],
            self.candles['Low'],
            self.candles['Close'],
            length=add_parametres['Period'],
            scalar=add_parametres['Scalar'],
            mamode=matype,
            offset=shift
        )
        columns_choices = ["lower", "basis", "upper"]
        values = self._get_indicator_values(
            add_parametres["Channel Type"],
            columns_choices,
            data
        )
        return values

    def get_adx(self, add_parametres, shift, matype):
        data = ta.adx(
            self.candles['High'],
            self.candles['Low'],
            self.candles['Close'],
            length=add_parametres['Period'],
            lensig=add_parametres['Signal Period'],
            scalar=add_parametres['Scalar'],
            mamode=matype,
            offset=shift
        )
        columns_choices = ["adx", "dmp", "dmn"]
        values = self._get_indicator_values(
            add_parametres["ADX Type"],
            columns_choices,
            data
        )
        return values

    def get_vortex(self, ap, shift):
        data = ta.vortex(
            self.candles['High'],
            self.candles['Low'],
            self.candles['Close'],
            length=ap['Period'],
            offset=shift
        )
        columns_choices = ["vip", "vim"]
        values = self._get_indicator_values(
            ap["Vortex Type"],
            columns_choices,
            data
        )
        return values

    def get_aroon(self, ap, shift):
        data = ta.aroon(
            self.candles['High'],
            self.candles['Low'],
            length=ap['Period'],
            scalar=ap['Scalar'],
            offset=shift
        )
        columns_choices = ["aroon_up", "aroon_down", "aroon_osc"]
        values = self._get_indicator_values(
            ap["Aroon Type"],
            columns_choices,
            data
        )
        return values

    def get_gann(self, ap, shift, ma_method):
        data = ta.hilo(
            self.candles['High'],
            self.candles['Low'],
            self.candles['Close'],
            high_length=ap['High Period'],
            low_length=ap['Low Period'],
            mamode=ma_method,
            offset=shift
        )
        columns_choices = ["HILO (line)", "HILOl (long)", "HILOs (short)"]
        values = self._get_indicator_values(
            ap["Indicator Type"],
            columns_choices,
            data
        )
        return values
