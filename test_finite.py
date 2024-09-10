import math

values = [
    "sadadad",
    "",
    0,
    123123213123131,
    0.00000000000001,
    True,
    False
]

for val in values:
    try:
        print(val, math.isfinite(val))
    except Exception:
        pass