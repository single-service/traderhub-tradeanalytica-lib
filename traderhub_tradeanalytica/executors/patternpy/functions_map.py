from .tradingpatterns import (
    detect_head_shoulder, detect_multiple_tops_bottoms, detect_triangle_pattern,
    detect_wedge, detect_channel, detect_double_top_bottom,
)


TRADEPATTERNS_MAP = {
    "Head And Shoulders": {
        "func": detect_head_shoulder,
        "result_column": "head_shoulder_pattern",
    },
    "Triangle": {
        "func": detect_triangle_pattern,
        "result_column": "triangle_pattern",
    },
    "Wedge": {
        "func": detect_wedge,
        "result_column": "wedge_pattern",
    },
    "Multiple Tops/Bottoms": {
        "func": detect_multiple_tops_bottoms,
        "result_column": "multiple_top_bottom_pattern",
    },
    "Channel": {
        "func": detect_channel,
        "result_column": "channel_pattern",
    },
    "Double Top/Bottom": {
        "func": detect_double_top_bottom,
        "result_column": "double_pattern",
    },
}