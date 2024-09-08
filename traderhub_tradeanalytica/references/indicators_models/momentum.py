from .constants import PRICES_CHOICES, LINES_CHOICES, MA_METHODS


MOMENTUM_PARAMS = {
    "Awesome Oscillator": [
        ("Fast", "int", 5, "fast",),
        ("Slow", "int", 34, "slow",),
        ("Shift", "int", 0, "offset",),
    ],
    "MACD": [
        ("Fast EMA", "int", 12, "fast",),
        ("Slow EMA", "int", 26, "slow",),
        ("MACD SMA", "int", 9, "signal",),
        ("Apply To", "select", PRICES_CHOICES, None,),
        ("Indicator Buffer", "select", LINES_CHOICES, None,),
        ("Shift", "int", 0, "offset",),
    ],
    "Momentum": [
        ("Period", "int", 14, "length",),
        ("Apply To", "select", PRICES_CHOICES, None,),
        ("Shift", "int", 0, "offset",),
    ],
    "Stohastic Oscillator": [
        ("%K Period", "int", 5, "k",),
        ("%D Period", "int", 3, "d"),
        ("Slowing", "int", 2, "smooth_k"),
        ("MA Method", "select", MA_METHODS, "mamode"),
        ("Price Field", "select", ["Low/High", "Close/Close"], None,),
        ("Indicator Buffer", "select", LINES_CHOICES, None,),
        ("Shift", "int", 0, "offset",),
    ],
    # NEW
    "Absolute Price Oscillator": [
        ("Fast", "int", 12, "fast"),
        ("Slow", "int", 26, "slow"),
        ("MA Method", "select", MA_METHODS, "mamode"),
        ("Shift", "int", 0, "offset"),
    ],
    "Relative Strength Index (RSI)": [
        ("Period", "int", 14, "length"),
        ("Scalar", "float", 100, "scalar"),
        ("Shift", "int", 0, "offset"),
    ],
    "Commodity Channel Index (CCI)": [
        ("Period", "int", 14, "length"),
        ("C", "float", 0.015, "c"),
        ("Shift", "int", 0, "offset"),
    ],
    "Fisher Transform": [
        ("Period", "int", 9, "length"),
        ("Signal Period", "int", 1, "signal"),
        ("Shift", "int", 0, "offset"),
    ],
    "Relative Vigor Index (RVGI)": [
        ("Period", "int", 14, "length"),
        ("SWMA Period", "int", 4, "swma_length"),
        ("Shift", "int", 0, "offset"),
    ],
    "True Strength Index (TSI)": [
        ("Fast", "int", 13, "fast"),
        ("Slow", "int", 25, "slow"),
        ("Signal Period", "int", 12, "signal"),
        ("Scalar", "float", 100, "scalar"),
        ("MA Method", "select", MA_METHODS, "mamode"),
        ("Indicator Type", "select", LINES_CHOICES, None),
        ("Shift", "int", 0, "offset"),
    ]
}