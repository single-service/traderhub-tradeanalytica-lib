from .constants import MA_METHODS, PRICES_CHOICES


OVERLAP_PARAMS = {
    "Moving Average": [
        ("Period", "int", 14, "length"),
        ("MA Method", "select", MA_METHODS, None),
        ("Apply To", "select", PRICES_CHOICES, None),
        ("Shift", "int", 0, "offset"),
    ],
    # NEW
    # "Zero Lag Moving Average": [ Сломанный
    #     ("Period", "int", 10,),
    #     ("MA Method", "select", MA_METHODS,),
    #     ("Shift", "int", 0,),
    # ],
    "Fibonacci's Weighted Moving Average": [
        ("Period", "int", 10, "length"),
        ("ASC", "bool", True, "asc"),
        ("Shift", "int", 0, "offset"),
    ],
    "Gann High-Low Activator": [
        ("High Period", "int", 13, "high_length"),
        ("Low Period", "int", 21, "low_length"),
        ("MA Method", "select", MA_METHODS, "mamode"),
        ("Indicator Type", "select", ["HILO (line)", "HILOl (long)", "HILOs (short)"], None),
        ("Shift", "int", 0, "offset"),
    ],
}