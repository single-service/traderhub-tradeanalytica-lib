from traderhub_tradeanalytica.references import GROUP_MODELS_MAP

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

print(ALL_INDICATORS_PARAMS)