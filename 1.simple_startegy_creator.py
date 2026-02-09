import json

from traderhub_tradeanalytica.references import GROUP_MODELS_MAP


Shift_combinations = [0, 1 ,2]
Window_combinations = [5, 10, 15, 20]

CONDITION_GROUPS = ["value", *GROUP_MODELS_MAP.keys()]
# print(GROUP_MODELS_MAP)
ALL_INDICATORS_PARAMS = {
    k: { # наименование группы
        i["name"]: { # наименование индикатора
            p["name"]: { # наименование параметра
                "type": p["type"],
                "options": p.get("selections"),
                "default": p.get("default")
            } for p in i["parametres"]
        } for i in v
    } for k, v in GROUP_MODELS_MAP.items()
}

PARAMS_COMBINATIONS = {}

for group_name, group_data in ALL_INDICATORS_PARAMS.items():
    if group_name in ["value", "price"]:
        continue
    PARAMS_COMBINATIONS[group_name] = {}
    for indicator_name, indicator_data in group_data.items():
        PARAMS_COMBINATIONS[group_name][indicator_name] = {}
        for param_name, param_data in indicator_data.items():
            values = []
            if param_data.get("options"):
                continue
                values = param_data["options"]
            if param_name in ["Shift", "Window"]:
                continue
            PARAMS_COMBINATIONS[group_name][indicator_name][param_name] = {
                "type": param_data["type"],
                "values": values
            }

with open("all_params.json", "w") as combinations_file:
    json.dump(ALL_INDICATORS_PARAMS, combinations_file, ensure_ascii=False, indent=4)
with open("combinations.json", "w") as combinations_file:
    json.dump(PARAMS_COMBINATIONS, combinations_file, ensure_ascii=False, indent=4)