#!/usr/bin/env python3
"""
Скрипт для генерации простых торговых стратегий.
Простая стратегия = один шаг + одно условие + тип сделки buy
"""

import json
from itertools import product
from pathlib import Path


# Константы
SHIFT_COMBINATIONS = [0, 1, 2]
WINDOW_COMBINATIONS = [5, 10, 15, 20]

# Директории
DICT_DIR = Path("dictionaries")
STRATEGIES_DIR = Path("strategies")
STRATEGIES_DIR.mkdir(exist_ok=True)


def load_dictionaries():
    """Загрузка всех необходимых словарей."""
    with open(DICT_DIR / "all_params.json", "r", encoding="utf-8") as f:
        all_params = json.load(f)

    with open(DICT_DIR / "param_combinations.json", "r", encoding="utf-8") as f:
        param_combinations = json.load(f)

    with open(DICT_DIR / "indicators_conditions.json", "r", encoding="utf-8") as f:
        indicators_conditions = json.load(f)

    with open(DICT_DIR / "self_comparison_params.json", "r", encoding="utf-8") as f:
        self_comparison_params = json.load(f)

    return all_params, param_combinations, indicators_conditions, self_comparison_params


def generate_strategy_name(indicator_name, params, comparison_type, comparison_value=None):
    """Генерация короткого имени стратегии."""
    # Сокращаем название индикатора
    short_name = indicator_name.replace(" ", "")[:15]

    # Добавляем ключевые параметры
    key_params = []
    for param_name, param_value in params.items():
        if param_name not in ["Shift"] and not isinstance(param_value, bool):
            key_params.append(f"{param_value}")

    # Формируем имя
    param_str = "_".join(key_params[:2]) if key_params else ""

    # Добавляем тип сравнения
    comp_str = ""
    if comparison_type == "self":
        comp_str = "self"
    elif comparison_type == "price":
        comp_str = comparison_value  # Ask или Bid
    elif comparison_type == "value":
        comp_str = f"v{comparison_value}"

    strategy_name = f"{short_name}_{param_str}_{comp_str}".replace("__", "_")

    return strategy_name[:50]  # Ограничиваем длину


def create_condition(group, indicator_name, left_params, right_group, right_value, operator):
    """Создание условия для стратегии."""
    condition = {
        "left_condition": {
            "group": group,
            "main_parametres": [
                {
                    "name": "name",
                    "value": indicator_name
                }
            ],
            "add_parametres": []
        },
        "right_condition": {},
        "conditions_delimiter": operator
    }

    # Добавляем параметры в left_condition
    for param_name, param_value in left_params.items():
        condition["left_condition"]["add_parametres"].append({
            "name": param_name,
            "value": param_value
        })

    # Формируем right_condition
    if right_group == "price":
        condition["right_condition"] = {
            "group": "price",
            "main_parametres": [
                {
                    "name": "name",
                    "value": right_value  # "Ask" или "Bid"
                }
            ],
            "add_parametres": []
        }
    elif right_group == "value":
        condition["right_condition"] = {
            "group": "value",
            "main_parametres": [
                {
                    "name": "Value",
                    "value": right_value
                },
                {
                    "name": "In pips",
                    "value": False
                }
            ],
            "add_parametres": []
        }
    elif right_group == "self":
        # Сравнение с самим собой (с другими параметрами)
        # right_value здесь - это словарь параметров для правой части
        condition["right_condition"] = {
            "group": group,
            "main_parametres": [
                {
                    "name": "name",
                    "value": indicator_name
                }
            ],
            "add_parametres": []
        }
        # Добавляем параметры из right_value
        for param_name, param_value in right_value.items():
            condition["right_condition"]["add_parametres"].append({
                "name": param_name,
                "value": param_value
            })

    return condition


def create_strategy_json(name, condition):
    """Создание полной структуры стратегии."""
    return {
        "lot": 0.1,
        "exit-deal": {
            "stop-loss-type": "fixed",
            "stop-loss-value": 50,
            "take-profit-type": "fixed",
            "take-profit-value": 150
        },
        "entry-deal": {
            "buy": [
                [condition]
            ],
            "sell": []
        }
    }


def save_strategy_to_file(strategy_name, strategy, file_counter):
    """Сохранение одной стратегии в файл."""
    # Делаем имя файла безопасным
    safe_name = strategy_name.replace(" ", "_").replace("/", "_")
    filename = f"{file_counter:06d}_{safe_name}.json"
    filepath = STRATEGIES_DIR / filename

    # Проверяем существование файла
    if filepath.exists():
        return False  # Файл уже существует, пропускаем

    # Сохраняем стратегию
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(strategy, f, indent=4, ensure_ascii=False)

    return True  # Файл успешно создан


def generate_indicator_strategies(all_params, param_combinations, indicators_conditions, self_comparison_params, file_counter):
    """Генерация стратегий для индикаторов."""
    strategies_count = 0

    for indicator_name in all_params["indicators"].keys():
        print(f"Обработка индикатора: {indicator_name}")

        if indicator_name not in indicators_conditions:
            print(f"  Пропуск: нет условий в indicators_conditions.json")
            continue

        # Получаем все параметры из all_params
        indicator_params_full = all_params["indicators"][indicator_name]

        # Собираем значения для каждого параметра
        param_values_dict = {}

        for param_name, param_info in indicator_params_full.items():
            param_type = param_info["type"]

            if param_name == "Shift":
                # Shift всегда [0, 1, 2]
                param_values_dict[param_name] = SHIFT_COMBINATIONS
            elif param_name == "Window":
                # Window всегда [5, 10, 15, 20]
                param_values_dict[param_name] = WINDOW_COMBINATIONS
            elif param_info.get("options"):
                # Параметры с options берем из all_params
                param_values_dict[param_name] = param_info["options"]
            elif param_type == "bool":
                # Bool параметры
                if indicator_name in param_combinations["indicators"] and \
                   param_name in param_combinations["indicators"][indicator_name]:
                    param_values_dict[param_name] = param_combinations["indicators"][indicator_name][param_name]["values"]
                else:
                    param_values_dict[param_name] = [True, False]
            elif param_type in ["int", "float"]:
                # Int/Float параметры берем из param_combinations
                if indicator_name in param_combinations["indicators"] and \
                   param_name in param_combinations["indicators"][indicator_name]:
                    param_values_dict[param_name] = param_combinations["indicators"][indicator_name][param_name]["values"]
                else:
                    # Если нет в param_combinations, пропускаем
                    print(f"  Предупреждение: параметр {param_name} не найден в param_combinations")

        # Генерируем все комбинации параметров
        if param_values_dict:
            param_names = list(param_values_dict.keys())
            param_values_lists = [param_values_dict[name] for name in param_names]

            all_param_combinations = list(product(*param_values_lists))
            print(f"  Всего комбинаций параметров: {len(all_param_combinations)}")

            # Получаем условия для этого индикатора
            conditions_list = indicators_conditions[indicator_name]

            for condition_type in conditions_list:
                if condition_type == "self":
                    # Сравнение с собой - комбинируем только указанные параметры
                    print(f"  Генерация условий 'self' для {indicator_name}...")

                    # Получаем параметры для комбинирования
                    params_to_vary = self_comparison_params.get(indicator_name, [])

                    if not params_to_vary:
                        print(f"    Нет параметров для комбинирования в 'self'")
                        continue

                    # Разделяем параметры на варьируемые и фиксированные
                    vary_param_names = [p for p in param_names if p in params_to_vary]
                    fixed_param_names = [p for p in param_names if p not in params_to_vary]

                    # Для варьируемых параметров создаем комбинации
                    vary_param_values_lists = [param_values_dict[name] for name in vary_param_names]
                    vary_combinations = list(product(*vary_param_values_lists))

                    # Для фиксированных параметров берем первое значение
                    fixed_params = {name: param_values_dict[name][0] for name in fixed_param_names}

                    print(f"    Варьируемые параметры: {vary_param_names}")
                    print(f"    Комбинаций для варьируемых параметров: {len(vary_combinations)}")

                    # Перебираем все пары комбинаций для варьируемых параметров
                    for i, left_vary_values in enumerate(vary_combinations):
                        left_params = fixed_params.copy()
                        left_params.update(dict(zip(vary_param_names, left_vary_values)))

                        for j, right_vary_values in enumerate(vary_combinations):
                            if i == j:
                                continue

                            right_params = fixed_params.copy()
                            right_params.update(dict(zip(vary_param_names, right_vary_values)))

                            for operator in [">", "<"]:
                                condition = create_condition(
                                    "indicators",
                                    indicator_name,
                                    left_params,
                                    "self",
                                    right_params,
                                    operator
                                )
                                strategy_name = generate_strategy_name(
                                    indicator_name, left_params, "self"
                                )
                                strategy = create_strategy_json(strategy_name, condition)

                                # Сохраняем сразу в файл
                                if save_strategy_to_file(strategy_name, strategy, file_counter):
                                    file_counter += 1
                                    strategies_count += 1

                elif condition_type == "price":
                    # Сравнение с ценой
                    print(f"  Генерация условий 'price' для {indicator_name}...")
                    for params_values in all_param_combinations:
                        params = dict(zip(param_names, params_values))

                        for price_type in ["Ask", "Bid"]:
                            for operator in [">", "<"]:
                                condition = create_condition(
                                    "indicators",
                                    indicator_name,
                                    params,
                                    "price",
                                    price_type,
                                    operator
                                )
                                strategy_name = generate_strategy_name(
                                    indicator_name, params, "price", price_type
                                )
                                strategy = create_strategy_json(strategy_name, condition)

                                # Сохраняем сразу в файл
                                if save_strategy_to_file(strategy_name, strategy, file_counter):
                                    file_counter += 1
                                    strategies_count += 1

                elif condition_type.startswith("value:"):
                    # Сравнение со значением
                    print(f"  Генерация условий 'value' для {indicator_name}...")
                    values_str = condition_type.split(":")[1]
                    values = [float(v) if '.' in v else int(v) for v in values_str.split(",")]

                    for params_values in all_param_combinations:
                        params = dict(zip(param_names, params_values))

                        for value in values:
                            for operator in [">", "<"]:
                                condition = create_condition(
                                    "indicators",
                                    indicator_name,
                                    params,
                                    "value",
                                    value,
                                    operator
                                )
                                strategy_name = generate_strategy_name(
                                    indicator_name, params, "value", value
                                )
                                strategy = create_strategy_json(strategy_name, condition)

                                # Сохраняем сразу в файл
                                if save_strategy_to_file(strategy_name, strategy, file_counter):
                                    file_counter += 1
                                    strategies_count += 1

            if strategies_count % 100 == 0 and strategies_count > 0:
                print(f"  Сохранено стратегий: {strategies_count}")

    return strategies_count, file_counter


def generate_candlestick_strategies(all_params, param_combinations, file_counter):
    """Генерация стратегий для свечных паттернов."""
    strategies_count = 0

    for pattern_name in param_combinations["candlestick_pattern"].keys():
        print(f"Обработка свечного паттерна: {pattern_name}")

        # Получаем параметры с options
        pattern_params = all_params["candlestick_pattern"].get(pattern_name, {})

        if pattern_params:
            # Есть параметр Type с options
            type_options = pattern_params.get("Type", {}).get("options", [])

            for type_value in type_options:
                params = {"Type": type_value}

                condition = create_condition(
                    "candlestick_pattern",
                    pattern_name,
                    params,
                    "value",
                    1,
                    "="
                )

                strategy_name = f"{pattern_name}_{type_value}"
                strategy = create_strategy_json(strategy_name, condition)

                if save_strategy_to_file(strategy_name, strategy, file_counter):
                    file_counter += 1
                    strategies_count += 1
        else:
            # Нет параметров
            params = {}

            condition = create_condition(
                "candlestick_pattern",
                pattern_name,
                params,
                "value",
                1,
                "="
            )

            strategy_name = pattern_name
            strategy = create_strategy_json(strategy_name, condition)

            if save_strategy_to_file(strategy_name, strategy, file_counter):
                file_counter += 1
                strategies_count += 1

    return strategies_count, file_counter


def generate_pattern_strategies(all_params, param_combinations, file_counter):
    """Генерация стратегий для графических паттернов."""
    strategies_count = 0

    for pattern_name in param_combinations["pattern"].keys():
        print(f"Обработка паттерна: {pattern_name}")

        # Получаем параметры
        pattern_params = all_params["pattern"].get(pattern_name, {})

        # Добавляем Window
        window_values = WINDOW_COMBINATIONS

        # Получаем Type options
        type_options = pattern_params.get("Type", {}).get("options", [])

        if type_options:
            for window in window_values:
                for type_value in type_options:
                    params = {
                        "Window": window,
                        "Type": type_value
                    }

                    condition = create_condition(
                        "pattern",
                        pattern_name,
                        params,
                        "value",
                        1,
                        "="
                    )

                    strategy_name = f"{pattern_name.replace(' ', '')}_{window}_{type_value.replace(' ', '')}"
                    strategy = create_strategy_json(strategy_name, condition)

                    if save_strategy_to_file(strategy_name, strategy, file_counter):
                        file_counter += 1
                        strategies_count += 1
        else:
            # Нет Type, только Window
            for window in window_values:
                params = {"Window": window}

                condition = create_condition(
                    "pattern",
                    pattern_name,
                    params,
                    "value",
                    1,
                    "="
                )

                strategy_name = f"{pattern_name.replace(' ', '')}_{window}"
                strategy = create_strategy_json(strategy_name, condition)

                if save_strategy_to_file(strategy_name, strategy, file_counter):
                    file_counter += 1
                    strategies_count += 1

    return strategies_count, file_counter




def main():
    """Главная функция."""
    print("=" * 60)
    print("Генератор простых торговых стратегий")
    print("=" * 60)

    # Загружаем словари
    print("\n1. Загрузка словарей...")
    all_params, param_combinations, indicators_conditions, self_comparison_params = load_dictionaries()
    print("   Словари загружены успешно")

    # Счетчик файлов
    file_counter = 1

    # Генерируем стратегии для индикаторов
    print("\n2. Генерация стратегий для индикаторов...")
    indicator_count, file_counter = generate_indicator_strategies(
        all_params, param_combinations, indicators_conditions, self_comparison_params, file_counter
    )
    print(f"   Создано {indicator_count} стратегий для индикаторов")

    # Генерируем стратегии для свечных паттернов
    print("\n3. Генерация стратегий для свечных паттернов...")
    candlestick_count, file_counter = generate_candlestick_strategies(
        all_params, param_combinations, file_counter
    )
    print(f"   Создано {candlestick_count} стратегий для свечных паттернов")

    # Генерируем стратегии для графических паттернов
    print("\n4. Генерация стратегий для графических паттернов...")
    pattern_count, file_counter = generate_pattern_strategies(
        all_params, param_combinations, file_counter
    )
    print(f"   Создано {pattern_count} стратегий для графических паттернов")

    # Итого
    total_count = indicator_count + candlestick_count + pattern_count
    print(f"\n5. Всего создано стратегий: {total_count}")
    print(f"   Все стратегии сохранены в директорию: {STRATEGIES_DIR}")

    print("\n" + "=" * 60)
    print("Генерация завершена!")
    print("=" * 60)


if __name__ == "__main__":
    main()
