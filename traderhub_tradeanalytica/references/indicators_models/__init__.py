from .cycles import CYCLES_PARAMS
from .momentum import MOMENTUM_PARAMS
from .overlap import OVERLAP_PARAMS
from .trend import TREND_PARAMS
from .volatility import VOLATILITY_PARAMS
from .volume import VOLUME_PARAMS


ALL_PARAMS = {
    **CYCLES_PARAMS,
    **MOMENTUM_PARAMS,
    **OVERLAP_PARAMS,
    **TREND_PARAMS,
    **VOLATILITY_PARAMS,
    **VOLUME_PARAMS
}

BASE_INDICATORS_MODEL = [
    {
        "name": name,
        "parametres": [
            {
                "name": parameter[0],
                "type": parameter[1],
                "selections": parameter[2] if parameter[1] == "select" else None,
                "default": parameter[2] if parameter[1] != "select" else None,
            } for parameter in parametres
        ]
    } for name, parametres in ALL_PARAMS.items()]

INDICATORS_MODEL = sorted(BASE_INDICATORS_MODEL, key=lambda indicator: indicator["name"])
