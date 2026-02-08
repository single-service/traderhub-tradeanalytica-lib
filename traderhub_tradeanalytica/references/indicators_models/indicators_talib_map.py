from . import ALL_PARAMS

TALIB_INDICATORS_MAP = {
    "Awesome Oscillator": "ao",
    "Average True Range": "atr",
    "Even Better Sinewave": "ebsw",
    "MACD": "macd",
    "Momentum": "mom",
    "Money Flow Index": "mfi",
    "Moving Average": None,
    "On Balance Volume": "obv",
    "Stohastic Oscillator": "stoch",
    "Absolute Price Oscillator": "apo",
    "Relative Strength Index (RSI)": "rsi",
    "Commodity Channel Index (CCI)": "cci",
    "Fisher Transform": "fisher",
    "Relative Vigor Index (RVGI)": "rvgi",
    "True Strength Index (TSI)": "tsi",
    "Aberration": "aberration",
    "Mass Index": "massi",
    "Donchian Channel": "donchain",
    "Keltner Channel": "kc",
    "Average Directional Index (ADX)": "adx",
    "Vertical Horizontal Filter": "vhf",
    "Vortex": "vortex",
    "Aroon": "aroon",
    "Accumulation/Distribution Index": "ad",
    "Chaikin Money Flow": "cmf",
    "Fibonacci's Weighted Moving Average": "fwma",
    "Gann High-Low Activator": "hilo",
}


def get_indicators_talib_data(indicator_name, additional_parametres):
    talib_indicator_name = TALIB_INDICATORS_MAP[indicator_name]
    ap_map = {x['name']: x['value'] for x in additional_parametres}
    if indicator_name == "Moving Average":
        ma_method = ap_map.get('MA Method', 'Exponential')
        ma_function = {
            "Simple": "sma",
            "Exponential": "ema",
            "Smoothed": "wma"
        }
        talib_indicator_name = ma_function.get(ma_method, "ema")
    indicator_data = {"kind": talib_indicator_name}
    indicator_parametres = ALL_PARAMS[indicator_name]
    key_values = [indicator_name]
    for ind_pm in indicator_parametres:
        # ind_pm[3] - pandas_ta parameter name (None means UI-only parameter)
        if ind_pm[3] is None:
            continue

        # Get parameter name and check if it exists in strategy
        param_name = ind_pm[0]  # Parameter name from ALL_PARAMS
        if param_name not in ap_map:
            # If parameter is missing, use default value
            default_value = ind_pm[2]
            indicator_data[ind_pm[3]] = default_value
            key_values.append(str(default_value))
        else:
            # If parameter exists, use its value
            indicator_data[ind_pm[3]] = ap_map[param_name]
            key_values.append(str(ap_map[param_name]))

    indicator_data["prefix"] = "".join(key_values)
    key = "_".join(key_values)
    return key, indicator_data


def get_prefix(indicator_name, additional_parametres):
    key_values = [indicator_name]
    ap_map = {x['name']: x['value'] for x in additional_parametres}
    indicator_parametres = ALL_PARAMS[indicator_name]
    for ind_pm in indicator_parametres:
        if ind_pm[3] is None:
            continue
        # Use default value if parameter is missing
        param_name = ind_pm[0]
        param_value = ap_map.get(param_name, ind_pm[2])
        key_values.append(str(param_value))
    prefix = "".join(key_values)
    return prefix


def find_indicator_column(columns, condition):
    indicator_name = condition['main_parametres'][0]['value']
    prefix = get_prefix(indicator_name, condition['add_parametres'])
    ap = {x['name']: x['value'] for x in condition['add_parametres']}
    filtered_columns = [x for x in columns if x.split("_")[0] == prefix]
    if indicator_name == "MACD":
        identifier = "MACD_" if ap['Indicator Buffer'] == "Base line" else "MACDs_"
        filtered_columns = [x for x in filtered_columns if identifier in x.replace(f"{prefix}_", "")]
    if indicator_name == "Stohastic Oscillator":
        # Support both "Line Type" and "Indicator Buffer" parameter names
        line_type = ap.get('Line Type', ap.get('Indicator Buffer', 'K'))
        identifier = "STOCHk_" if line_type in ("K", "Base line") else "STOCHd_"
        filtered_columns = [x for x in filtered_columns if identifier in x.replace(f"{prefix}_", "")]
    if indicator_name == "True Strength Index (TSI)":
        identifier = "TSI_" if ap['Indicator Type'] == "Base line" else "TSIs_"
        filtered_columns = [x for x in filtered_columns if identifier in x.replace(f"{prefix}_", "")]
    if indicator_name == "Gann High-Low Activator":
        identifier = "HILO_"
        if ap["Indicator Type"] == "HILOl (long)":
            identifier = "HILOl_"
        if ap["Indicator Type"] == "HILOs (short)":
            identifier = "HILOs_"
        filtered_columns = [x for x in filtered_columns if identifier in x.replace(f"{prefix}_", "")]
    if indicator_name == "Average Directional Index (ADX)":
        afx_type = ap["ADX Type"]
        identifier = f"{afx_type.upper()}_"
        filtered_columns = [x for x in filtered_columns if identifier in x.replace(f"{prefix}_", "")]
    if indicator_name == "Vortex":
        identifier = "VTXP_" if ap["Vortex Type"] == "vip" else "VTXM_"
        filtered_columns = [x for x in filtered_columns if identifier in x.replace(f"{prefix}_", "")]
    if indicator_name == "Aroon":
        identifier = "AROONU_"
        if ap["Aroon Type"] == "aroon_down":
            identifier = "AROOND_"
        if ap["Aroon Type"] == "aroon_osc":
            identifier = "AROONOSC_"
        filtered_columns = [x for x in filtered_columns if identifier in x.replace(f"{prefix}_", "")]
    if indicator_name == "Donchian Channel":
        donchain_type = ap['Donchian Type']
        identifier = f"DC{donchain_type[0].upper()}_"
        filtered_columns = [x for x in filtered_columns if identifier in x.replace(f"{prefix}_", "")]
    if indicator_name == "Keltner Channel":
        channel_type = ap['Channel Type']
        identifier = f"KC{channel_type[0].upper()}e_"
        filtered_columns = [x for x in filtered_columns if identifier in x.replace(f"{prefix}_", "")]
    if indicator_name == "Aberration":
        abb_type = ap['ATR Type']
        identifier = f"ABER_{abb_type.upper()}_"
        filtered_columns = [x for x in filtered_columns if identifier in x.replace(f"{prefix}_", "")]
    if len(filtered_columns) == 0:
        return None
    return filtered_columns[0]