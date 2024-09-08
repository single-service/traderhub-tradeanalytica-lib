
from .cdl_pattern_models import CANDLESTICKPATTERN_MODEL
from .indicators_models import INDICATORS_MODEL
from .pattern_models import PATTERN_MODEL
from .price_models import PRICE_MODEL


CONDITIONS_GROUPS = {
    "indicators": {
        "parametres": [
            {
                "name": "Indicator",
                "type": "from_model"
            }
        ]
    },
    "price": {
        "parametres": [
            {
                "name": "Price",
                "type": "from_model"
            }
        ]
    },
    "candlestick": {
        "parametres": [
            {
                "name": "Timeframe",
                "type": "select",
                "selections": [
                    "Current",
                    "M30",
                    "H1",
                    "H4",
                    "D1",
                    "W1",
                    "MN1"
                ]
            },
            {
                "name": "Candlestick Index",
                "type": "int",
                "default": 0
            },
            {
                "name": "Candlestick Value",
                "type": "select",
                "selections": [
                    "Open",
                    "High",
                    "Low",
                    "Close",
                    "Range",
                    "Body length",
                    "Upper wick",
                    "Lower wick"
                ]
            }
        ]
    },
    "candlestick_pattern": {
        "parametres": [
            {
                "name": "Pattern",
                "type": "from_model"
            }
        ]
    },
    "pattern": {
        "parametres": [
            {
                "name": "Pattern",
                "type": "from_model"
            }
        ]
    },
    "value": {
        "parametres": [
            {
                "name": "Value",
                "type": "int",
                "default": 0
            },
            {
                "name": "In pips",
                "type": "bool",
                "default": False
            }
        ]
    }
}

GROUP_MODELS_MAP = {
    "indicators": INDICATORS_MODEL,
    "price": PRICE_MODEL,
    "candlestick_pattern": CANDLESTICKPATTERN_MODEL,
    "pattern": PATTERN_MODEL
}