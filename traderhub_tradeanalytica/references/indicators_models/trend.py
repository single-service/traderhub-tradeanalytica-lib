from .constants import MA_METHODS


TREND_PARAMS = {
    #NEW
    "Average Directional Index (ADX)": [
        ("Period", "int", 14, "length"),
        ("Signal Period", "int", 14, "lensig"),
        ("Scalar", "float", 100, "scalar"),
        ("MA Method", "select", MA_METHODS, "mamode"),
        ("ADX Type", "select", ["adx", "dmp", "dmn"], None),
        ("Shift", "int", 0, "offset"),
    ],
    "Vertical Horizontal Filter": [
        ("Period", "int", 14, "length"),
        ("Shift", "int", 0, "offset"),
    ],
    "Vortex": [
        ("Period", "int", 14, "length"),
        ("Vortex Type", "select", ["vip" , "vim"], None),
        ("Shift", "int", 0, "offset"),
    ],
    "Aroon": [
        ("Period", "int", 14, "length"),
        ("Scalar", "float", 100, "scalar"),
        ("Aroon Type", "select", ["aroon_up", "aroon_down", "aroon_osc"], None),
        ("Shift", "int", 0, "offset"),
    ],
}