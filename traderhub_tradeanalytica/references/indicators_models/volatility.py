from .constants import MA_METHODS


VOLATILITY_PARAMS = {
    "Average True Range": [
        ("Period", "int", 14, "length"),
        ("Shift", "int", 0, "offset"),
    ],
    # NEW
    "Aberration": [
        ("Period", "int", 5, "length"),
        ("ATR Period", "int", 15, "atr_length"),
        ("ATR Type", "select", ["zg", "sg", "xg", "atr"], None),
        ("Shift", "int", 0, "offset"),
    ],
    "Donchian Channel": [
        ("Low Period", "int", 20, "lower_length"),
        ("Up Period", "int", 20, "upper_length"),
        ("Donchian Type", "select", ["lower", "mid", "upper"], None),
        ("Shift", "int", 0, "offset"),
    ],
    "Mass Index": [
        ("Fast", "int", 9, "fast"),
        ("Slow", "int", 25, "slow"),
        ("Shift", "int", 0, "offset"),
    ],
    "Keltner Channel": [
        ("Period", "int", 20, "length"),
        ("Scalar", "float", 2, "scalar"),
        ("MA Method", "select", MA_METHODS, "mamode"),
        ("Channel Type", "select", ["lower", "basis", "upper"], None),
        ("Shift", "int", 0, "offset",),
    ],
}