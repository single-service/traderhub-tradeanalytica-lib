from .constants import PRICES_CHOICES, MA_METHODS, LINES_CHOICES


VOLUME_PARAMS = {
    "Money Flow Index": [
        ("Period", "int", 14, "length"),
        ("Shift", "int", 0, "offset"),
    ],
    "On Balance Volume": [
        ("Apply To", "select", PRICES_CHOICES, None),
        ("Shift", "int", 0, "offset"),
    ],
    # NEW
    "Accumulation/Distribution Index": [
        ("Shift", "int", 0, "offset"),
    ],
    "Chaikin Money Flow": [
        ("Period", "int", 20, "length"),
        ("Shift", "int", 0, "offset"),
    ],
    # "Klinger Volume Oscillator": [ Сломанный
    #     ("Fast Period", "int", 34,),
    #     ("Long Period", "int", 45,),
    #     ("Signal Period", "int", 13,),
    #     ("MA Method", "select", MA_METHODS),
    #     ("Indicator Type", "select", LINES_CHOICES,),
    #     ("Shift", "int", 0,),
    # ],
}