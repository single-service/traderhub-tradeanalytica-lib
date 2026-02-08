"""
Визуальный конструктор торговых стратегий для TraderHub TradeAnalytica
"""
import json
import os
from pathlib import Path
from datetime import datetime
import streamlit as st
import pandas as pd
from traderhub_tradeanalytica import BacktestStrategyProcessor

from traderhub_tradeanalytica.references import GROUP_MODELS_MAP
from traderhub_tradeanalytica.references.indicators_models import INDICATORS_MODEL
from traderhub_tradeanalytica.references.cdl_pattern_models import CANDLESTICKPATTERN_MODEL

# Конфигурация страницы
st.set_page_config(
    page_title="TraderHub Strategy Constructor",
    page_icon="📈",
    layout="wide"
)

# Константы
STRATEGIES_DIR = Path("strategies")
STRATEGIES_DIR.mkdir(exist_ok=True)

METRICS_DIR = Path("metrics")
METRICS_DIR.mkdir(exist_ok=True)
METRICS_FILE = METRICS_DIR / "metrics.json"


# print(INDICATORS_MODEL)
# Доступные индикаторы
INDICATORS = [x["name"] for x in INDICATORS_MODEL]

# Параметры индикаторов
INDICATOR_PARAMS = {
    x["name"]: {
        p["name"]: {
            "type": p["type"],
            "options": p["selections"],
            "default": p["default"]
        } for p in  x["parametres"]
    }
    for x in INDICATORS_MODEL
}

CANDLESTICKS = [x["name"] for x in CANDLESTICKPATTERN_MODEL]



# {
#     "Moving Average": {
#         "Period": {"type": "int", "default": 14},
#         "MA Method": {"type": "select", "options": ["Simple", "Exponential", "Smoothed"], "default": "Exponential"},
#         "Apply To": {"type": "select", "options": ["Close", "Open", "High", "Low"], "default": "Close"},
#     },
#     "Stohastic Oscillator": {
#         "K": {"type": "int", "default": 5},
#         "D": {"type": "int", "default": 3},
#         "Smooth K": {"type": "int", "default": 3},
#         "Line Type": {"type": "select", "options": ["K", "D"], "default": "K"},
#     },
#     "MACD": {
#         "Fast EMA": {"type": "int", "default": 12},
#         "Slow EMA": {"type": "int", "default": 26},
#         "MACD SMA": {"type": "int", "default": 9},
#         "Indicator Buffer": {"type": "select", "options": ["Base line", "Signal line"], "default": "Base line"},
#     },
#     "RSI (Relative Strength Index)": {
#         "Period": {"type": "int", "default": 14},
#         "Scalar": {"type": "float", "default": 100.0},
#     },
# }


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
# print("GROUP_MODELS_MAP", json.dumps(GROUP_MODELS_MAP["indicators"][0]))
print(ALL_INDICATORS_PARAMS, ALL_INDICATORS_PARAMS)

# Операторы сравнения
COMPARISON_OPERATORS = ["<", ">", "=", "!=", ">=", "<="]


def load_strategies():
    """Загрузить все стратегии из директории"""
    strategies = []
    for file_path in STRATEGIES_DIR.glob("*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                strategy = json.load(f)
                strategy['_filename'] = file_path.name
                strategy['_filepath'] = str(file_path)
                strategies.append(strategy)
        except Exception as e:
            st.error(f"Ошибка загрузки {file_path.name}: {e}")
    return strategies


def save_strategy(strategy, filename):
    """Сохранить стратегию в JSON файл"""
    filepath = STRATEGIES_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(strategy, f, indent=4, ensure_ascii=False)
    return filepath


def delete_strategy(filepath):
    """Удалить стратегию"""
    Path(filepath).unlink()


def load_metrics():
    """Загрузить метрики всех стратегий"""
    if not METRICS_FILE.exists():
        return {}

    try:
        with open(METRICS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Ошибка загрузки метрик: {e}")
        return {}


def save_metrics(metrics):
    """Сохранить метрики стратегий"""
    try:
        with open(METRICS_FILE, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=4, ensure_ascii=False)
    except Exception as e:
        st.error(f"Ошибка сохранения метрик: {e}")


def update_strategy_metrics(strategy_filename, trade_type, metrics_data):
    """Обновить метрики для конкретной стратегии и типа сделки"""
    all_metrics = load_metrics()

    if strategy_filename not in all_metrics:
        all_metrics[strategy_filename] = {}

    all_metrics[strategy_filename][trade_type] = metrics_data
    all_metrics[strategy_filename]['last_backtest'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    save_metrics(all_metrics)


def create_condition_ui(key_prefix, condition_data=None):
    """Создать UI для одного условия"""
    condition = condition_data or {}

    col1, col2, col3 = st.columns([2, 1, 2])

    with col1:
        st.markdown("**Левое условие**")
        left_group = st.selectbox(
            "Тип",
            CONDITION_GROUPS,
            key=f"{key_prefix}_left_group",
            index=CONDITION_GROUPS.index(condition.get('left_condition', {}).get('group', 'value'))
        )

        left_condition = create_condition_side_ui(
            f"{key_prefix}_left",
            left_group,
            condition.get('left_condition')
        )

    with col2:
        st.markdown("**Оператор**")
        st.write("")  # spacing
        delimiter = st.selectbox(
            "Сравнение",
            COMPARISON_OPERATORS,
            key=f"{key_prefix}_delimiter",
            index=COMPARISON_OPERATORS.index(condition.get('conditions_delimiter', '<'))
        )

    with col3:
        st.markdown("**Правое условие**")
        right_group = st.selectbox(
            "Тип",
            CONDITION_GROUPS,
            key=f"{key_prefix}_right_group",
            index=CONDITION_GROUPS.index(condition.get('right_condition', {}).get('group', 'value'))
        )

        right_condition = create_condition_side_ui(
            f"{key_prefix}_right",
            right_group,
            condition.get('right_condition')
        )

    return {
        "left_condition": left_condition,
        "right_condition": right_condition,
        "conditions_delimiter": delimiter
    }

def create_group_side_ui(key_prefix, group):
    main_values = [x["name"] for x in GROUP_MODELS_MAP[group]]
    indicator = st.selectbox(
        f"{group} Name",
        main_values,
        key=f"{key_prefix}_indicator"
    )
    main_parametres = [{"name": "name", "value": indicator}]
    add_parametres = []
    if indicator in ALL_INDICATORS_PARAMS[group]:
        st.markdown("*Параметры индикатора:*")
        
        for param_name, param_config in ALL_INDICATORS_PARAMS[group][indicator].items():
            if param_config["type"] == "int":
                value = st.number_input(
                    param_name,
                    value=param_config["default"],
                    key=f"{key_prefix}_{param_name}",
                    min_value=0
                )
            elif param_config["type"] == "float":
                value = st.number_input(
                    param_name,
                    value=float(param_config["default"]),
                    key=f"{key_prefix}_{param_name}",
                    min_value=0.0
                )
            elif param_config["type"] == "select":
                index_val = 0
                if param_config.get("default"):
                    index_val = param_config["options"].index(param_config["default"])
                value = st.selectbox(
                    param_name,
                    param_config["options"],
                    key=f"{key_prefix}_{param_name}",
                    index=index_val
                )

            add_parametres.append({"name": param_name, "value": value})
    return {
        "group": group,
        "main_parametres": main_parametres,
        "add_parametres": add_parametres
    }

def create_condition_side_ui(key_prefix, group, condition_data=None):
    """Создать UI для одной стороны условия"""
    condition_data = condition_data or {}
    # if group == "indicators":
    #     indicator = st.selectbox(
    #         "Индикатор",
    #         INDICATORS,
    #         key=f"{key_prefix}_indicator"
    #     )

    #     main_parametres = [{"name": "Indicator", "value": indicator}]
    #     add_parametres = []

    #     # Параметры индикатора
    #     if indicator in INDICATOR_PARAMS:
    #         st.markdown("*Параметры индикатора:*")
    #         for param_name, param_config in INDICATOR_PARAMS[indicator].items():
    #             if param_config["type"] == "int":
    #                 value = st.number_input(
    #                     param_name,
    #                     value=param_config["default"],
    #                     key=f"{key_prefix}_{param_name}",
    #                     min_value=0
    #                 )
    #             elif param_config["type"] == "float":
    #                 value = st.number_input(
    #                     param_name,
    #                     value=float(param_config["default"]),
    #                     key=f"{key_prefix}_{param_name}",
    #                     min_value=0.0
    #                 )
    #             elif param_config["type"] == "select":
    #                 index_val = 0
    #                 if param_config.get("default"):
    #                     index_val = param_config["options"].index(param_config["default"])
    #                 value = st.selectbox(
    #                     param_name,
    #                     param_config["options"],
    #                     key=f"{key_prefix}_{param_name}",
    #                     index=index_val
    #                 )

    #             add_parametres.append({"name": param_name, "value": value})

    #     return {
    #         "group": "indicators",
    #         "main_parametres": main_parametres,
    #         "add_parametres": add_parametres
    #     }
    if group != "value":
        return create_group_side_ui(key_prefix, group)
    elif group == "value":
        value = st.number_input(
            "Значение",
            value=0.0,
            key=f"{key_prefix}_value"
        )
        in_pips = st.checkbox(
            "В пипсах",
            key=f"{key_prefix}_in_pips"
        )

        return {
            "group": "value",
            "main_parametres": [
                {"name": "Value", "value": value},
                {"name": "In pips", "value": in_pips}
            ],
            "add_parametres": []
        }

    # elif group == "price":
    #     price_type = st.selectbox(
    #         "Тип цены",
    #         ["Ask", "Bid"],
    #         key=f"{key_prefix}_price_type"
    #     )

    #     return {
    #         "group": "price",
    #         "main_parametres": [{"name": "Price", "value": price_type}],
    #         "add_parametres": []
    #     }

    # elif group == "candlestick":
    #     candle_index = st.number_input(
    #         "Индекс свечи (0 = текущая)",
    #         value=0,
    #         min_value=0,
    #         key=f"{key_prefix}_candle_index"
    #     )
    #     candle_value = st.selectbox(
    #         "Значение свечи",
    #         ["Open", "High", "Low", "Close", "Range", "Body length", "Upper wick", "Lower wick"],
    #         key=f"{key_prefix}_candle_value"
    #     )

    #     return {
    #         "group": "candlestick",
    #         "main_parametres": [
    #             {"name": "Candlestick Index", "value": int(candle_index)},
    #             {"name": "Candlestick Value", "value": candle_value}
    #         ],
    #         "add_parametres": []
    #     }

    return {}


def strategy_builder_page():
    """Страница создания новой стратегии"""
    st.header("📝 Создать новую стратегию")

    # Основные параметры стратегии
    st.subheader("Основные параметры")
    col1, col2 = st.columns(2)

    with col1:
        strategy_name = st.text_input("Название стратегии", "my_strategy")
        lot_size = st.number_input("Размер лота", value=0.1, min_value=0.01, step=0.01)

    with col2:
        st.write("")  # spacing

    # Exit deal параметры
    st.subheader("Условия выхода из сделки")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Stop Loss**")
        sl_type = st.selectbox("Тип Stop Loss", ["fixed", "dynamic"], key="sl_type")
        sl_value = st.number_input("Значение Stop Loss (пункты)", value=50, min_value=1, key="sl_value")

    with col2:
        st.markdown("**Take Profit**")
        tp_type = st.selectbox("Тип Take Profit", ["fixed", "dynamic", "relative"], key="tp_type")
        tp_value = st.number_input("Значение Take Profit", value=3, min_value=1, key="tp_value")
        if tp_type == "relative":
            st.info("Значение = множитель от Stop Loss")

    # Entry deal - Buy условия
    st.subheader("Условия входа - Buy сделки")

    if 'buy_steps' not in st.session_state:
        st.session_state.buy_steps = [[]]  # Один шаг с пустым условием

    buy_conditions = []
    for step_idx, step in enumerate(st.session_state.buy_steps):
        with st.expander(f"Шаг {step_idx + 1}", expanded=True):
            st.markdown(f"**Шаг {step_idx + 1}** (все условия должны выполниться)")

            step_conditions = []
            num_conditions = st.number_input(
                "Количество условий в шаге",
                min_value=1,
                value=max(1, len(step)),
                key=f"buy_step_{step_idx}_num"
            )

            for cond_idx in range(int(num_conditions)):
                st.markdown(f"*Условие {cond_idx + 1}*")
                condition = create_condition_ui(f"buy_s{step_idx}_c{cond_idx}")
                step_conditions.append(condition)
                st.divider()

            buy_conditions.append(step_conditions)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Добавить шаг для Buy"):
            st.session_state.buy_steps.append([])
            st.rerun()
    with col2:
        if len(st.session_state.buy_steps) > 1:
            if st.button("➖ Удалить последний шаг Buy"):
                st.session_state.buy_steps.pop()
                st.rerun()

    # Entry deal - Sell условия
    st.subheader("Условия входа - Sell сделки")

    if 'sell_steps' not in st.session_state:
        st.session_state.sell_steps = [[]]

    sell_conditions = []
    for step_idx, step in enumerate(st.session_state.sell_steps):
        with st.expander(f"Шаг {step_idx + 1}", expanded=True):
            st.markdown(f"**Шаг {step_idx + 1}** (все условия должны выполниться)")

            step_conditions = []
            num_conditions = st.number_input(
                "Количество условий в шаге",
                min_value=1,
                value=max(1, len(step)),
                key=f"sell_step_{step_idx}_num"
            )

            for cond_idx in range(int(num_conditions)):
                st.markdown(f"*Условие {cond_idx + 1}*")
                condition = create_condition_ui(f"sell_s{step_idx}_c{cond_idx}")
                step_conditions.append(condition)
                st.divider()

            sell_conditions.append(step_conditions)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Добавить шаг для Sell"):
            st.session_state.sell_steps.append([])
            st.rerun()
    with col2:
        if len(st.session_state.sell_steps) > 1:
            if st.button("➖ Удалить последний шаг Sell"):
                st.session_state.sell_steps.pop()
                st.rerun()

    # Сохранение стратегии
    st.divider()
    if st.button("💾 Сохранить стратегию", type="primary", use_container_width=True):
        strategy = {
            "lot": lot_size,
            "exit-deal": {
                "stop-loss-type": sl_type,
                "stop-loss-value": sl_value,
                "take-profit-type": tp_type,
                "take-profit-value": tp_value
            },
            "entry-deal": {
                "buy": buy_conditions,
                "sell": sell_conditions
            }
        }

        filename = f"{strategy_name}.json"
        filepath = save_strategy(strategy, filename)
        st.success(f"✅ Стратегия сохранена: {filepath}")

        # Показать JSON
        with st.expander("Просмотр JSON"):
            st.json(strategy)


def strategies_list_page():
    """Страница со списком стратегий"""
    st.header("📚 Список стратегий")

    strategies = load_strategies()
    all_metrics = load_metrics()

    if not strategies:
        st.info("Нет сохраненных стратегий. Создайте новую стратегию!")
        return

    st.write(f"Найдено стратегий: {len(strategies)}")

    # Создать таблицу с данными
    table_data = []
    for strategy in strategies:
        filename = strategy.get('_filename', 'Unknown')
        metrics = all_metrics.get(filename, {})

        # Базовая информация
        row = {
            'Стратегия': filename,
            'is_backtested': '✅' if metrics else '❌',
            'Лот': strategy.get('lot', 'N/A'),
            'SL Type': strategy.get('exit-deal', {}).get('stop-loss-type', 'N/A'),
            'SL Value': strategy.get('exit-deal', {}).get('stop-loss-value', 'N/A'),
            'TP Type': strategy.get('exit-deal', {}).get('take-profit-type', 'N/A'),
            'TP Value': strategy.get('exit-deal', {}).get('take-profit-value', 'N/A'),
        }

        # Метрики для Buy
        if 'buy' in metrics:
            buy_metrics = metrics['buy']
            buy_additional = buy_metrics.get('additional_metrics', {}) or {}
            row['Buy Сделок'] = buy_metrics.get('full_deals_cnt', 0)
            row['Buy Прибыль'] = round(buy_metrics.get('full_deals_saldo', 0), 2)
            row['Buy Винрейт %'] = round(buy_additional.get('win_rate', 0), 2)
            row['Buy PF'] = round(buy_additional.get('profit_factor', 0), 2)
        else:
            row['Buy Сделок'] = '-'
            row['Buy Прибыль'] = '-'
            row['Buy Винрейт %'] = '-'
            row['Buy PF'] = '-'

        # Метрики для Sell
        if 'sell' in metrics:
            sell_metrics = metrics['sell']
            sell_additional = sell_metrics.get('additional_metrics', {}) or {}
            row['Sell Сделок'] = sell_metrics.get('full_deals_cnt', 0)
            row['Sell Прибыль'] = round(sell_metrics.get('full_deals_saldo', 0), 2)
            row['Sell Винрейт %'] = round(sell_additional.get('win_rate', 0), 2)
            row['Sell PF'] = round(sell_additional.get('profit_factor', 0), 2)
        else:
            row['Sell Сделок'] = '-'
            row['Sell Прибыль'] = '-'
            row['Sell Винрейт %'] = '-'
            row['Sell PF'] = '-'

        # Последний бэктест
        row['Последний бэктест'] = metrics.get('last_backtest', '-')

        table_data.append(row)

    # Создать DataFrame
    df = pd.DataFrame(table_data)

    # Опции сортировки
    st.subheader("Настройки отображения")
    col1, col2 = st.columns(2)

    with col1:
        sort_by = st.selectbox(
            "Сортировать по:",
            ['Стратегия', 'Buy Прибыль', 'Sell Прибыль', 'Buy Винрейт %', 'Sell Винрейт %',
             'Buy PF', 'Sell PF', 'Последний бэктест'],
            key="sort_by"
        )

    with col2:
        sort_order = st.selectbox(
            "Порядок:",
            ['По возрастанию', 'По убыванию'],
            key="sort_order"
        )

    # Сортировка
    ascending = sort_order == 'По возрастанию'
    try:
        # Преобразуем столбец для сортировки, заменяя '-' на None
        if sort_by != 'Стратегия' and sort_by != 'Последний бэктест' and sort_by != 'is_backtested':
            df_sorted = df.copy()
            df_sorted[sort_by] = pd.to_numeric(df_sorted[sort_by], errors='coerce')
            df_sorted = df_sorted.sort_values(by=sort_by, ascending=ascending, na_position='last')
        else:
            df_sorted = df.sort_values(by=sort_by, ascending=ascending)
    except Exception:
        df_sorted = df

    # Показать таблицу
    st.dataframe(
        df_sorted,
        use_container_width=True,
        hide_index=True,
        height=min(400, len(df_sorted) * 35 + 38)  # Динамическая высота
    )

    # Детали и действия для каждой стратегии
    st.divider()
    st.subheader("Детали стратегий")

    for idx, strategy in enumerate(strategies):
        filename = strategy.get('_filename', f'Strategy {idx+1}')
        metrics = all_metrics.get(filename, {})

        with st.expander(f"📈 {filename} {'✅' if metrics else '❌'}", expanded=False):
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.markdown("**Основные параметры:**")
                st.write(f"- Лот: {strategy.get('lot', 'N/A')}")
                st.write(f"- Stop Loss: {strategy.get('exit-deal', {}).get('stop-loss-type')} = {strategy.get('exit-deal', {}).get('stop-loss-value')}")
                st.write(f"- Take Profit: {strategy.get('exit-deal', {}).get('take-profit-type')} = {strategy.get('exit-deal', {}).get('take-profit-value')}")

                buy_steps = len(strategy.get('entry-deal', {}).get('buy', []))
                sell_steps = len(strategy.get('entry-deal', {}).get('sell', []))
                st.write(f"- Buy шагов: {buy_steps}")
                st.write(f"- Sell шагов: {sell_steps}")

                # Показать метрики если есть
                if metrics:
                    st.markdown(f"**Последний бэктест:** {metrics.get('last_backtest', 'N/A')}")

            with col2:
                if st.button("🗑️ Удалить", key=f"delete_{idx}"):
                    delete_strategy(strategy['_filepath'])
                    # Также удалить метрики
                    if filename in all_metrics:
                        del all_metrics[filename]
                        save_metrics(all_metrics)
                    st.success("Стратегия удалена")
                    st.rerun()

            with col3:
                if st.button("📄 JSON", key=f"json_{idx}"):
                    st.session_state[f"show_json_{idx}"] = not st.session_state.get(f"show_json_{idx}", False)

            # Показать JSON если кнопка нажата
            if st.session_state.get(f"show_json_{idx}", False):
                # Убираем служебные поля
                display_strategy = {k: v for k, v in strategy.items() if not k.startswith('_')}
                st.json(display_strategy)


def backtest_page():
    """Страница бэктестирования стратегий"""
    st.header("🚀 Бэктест стратегии")

    strategies = load_strategies()

    if not strategies:
        st.warning("Нет сохраненных стратегий. Сначала создайте стратегию!")
        return

    # Выбор стратегии
    st.subheader("1. Выберите стратегию")
    strategy_names = [s.get('_filename', f"Strategy {i+1}") for i, s in enumerate(strategies)]
    selected_strategy_name = st.selectbox(
        "Стратегия",
        strategy_names,
        key="backtest_strategy_select"
    )

    selected_idx = strategy_names.index(selected_strategy_name)
    selected_strategy = strategies[selected_idx]

    # Показать параметры стратегии
    with st.expander("📊 Параметры выбранной стратегии", expanded=False):
        display_strategy = {k: v for k, v in selected_strategy.items() if not k.startswith('_')}
        st.json(display_strategy)

    # Загрузка данных
    st.subheader("2. Загрузите данные")

    # Опция: использовать тестовые данные или загрузить свои
    data_source = st.radio(
        "Источник данных",
        ["Использовать тестовые данные", "Загрузить CSV файл"],
        key="data_source"
    )

    candles = None

    if data_source == "Использовать тестовые данные":
        test_data_path = Path("test_data/EURUSD_60_2016-01-01_2024-06-01.csv")
        if test_data_path.exists():
            try:
                candles = pd.read_csv(
                    test_data_path,
                    names=['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume'],
                    index_col=False
                )
                candles['Datetime'] = pd.to_datetime(
                    candles['Date'] + ' ' + candles['Time'],
                    format='%Y.%m.%d %H:%M'
                )
                candles.drop(columns=['Date', 'Time'], inplace=True)
                candles = candles[~candles.index.duplicated(keep='first')]
                candles.set_index('Datetime', inplace=True)

                st.success(f"✅ Загружено {len(candles)} свечей из тестовых данных")

                # Показать превью данных
                with st.expander("👀 Превью данных (первые 10 строк)"):
                    st.dataframe(candles.head(10))

            except Exception as e:
                st.error(f"Ошибка загрузки тестовых данных: {e}")
        else:
            st.error(f"Тестовые данные не найдены: {test_data_path}")

    else:
        uploaded_file = st.file_uploader(
            "Выберите CSV файл с данными",
            type=['csv'],
            key="csv_upload"
        )

        if uploaded_file is not None:
            try:
                # Определить формат CSV
                col1, col2 = st.columns(2)
                with col1:
                    csv_format = st.selectbox(
                        "Формат CSV",
                        ["MetaTrader (Date, Time, Open, High, Low, Close, Volume)",
                         "Стандартный (Datetime, Open, High, Low, Close, Volume)"],
                        key="csv_format"
                    )

                if csv_format.startswith("MetaTrader"):
                    candles = pd.read_csv(
                        uploaded_file,
                        names=['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume'],
                        index_col=False
                    )
                    candles['Datetime'] = pd.to_datetime(
                        candles['Date'] + ' ' + candles['Time'],
                        format='%Y.%m.%d %H:%M'
                    )
                    candles.drop(columns=['Date', 'Time'], inplace=True)
                else:
                    candles = pd.read_csv(uploaded_file)
                    candles['Datetime'] = pd.to_datetime(candles['Datetime'])

                candles = candles[~candles.index.duplicated(keep='first')]
                candles.set_index('Datetime', inplace=True)

                st.success(f"✅ Загружено {len(candles)} свечей")

                # Показать превью данных
                with st.expander("👀 Превью данных (первые 10 строк)"):
                    st.dataframe(candles.head(10))

            except Exception as e:
                st.error(f"Ошибка загрузки файла: {e}")

    if candles is None:
        return

    # Параметры бэктеста
    st.subheader("3. Параметры бэктестирования")

    col1, col2, col3 = st.columns(3)

    with col1:
        point = st.number_input(
            "Point (минимальное изменение цены)",
            value=0.0001,
            format="%.5f",
            key="backtest_point"
        )

    with col2:
        spread_pips = st.number_input(
            "Spread (в пипсах)",
            value=15,
            min_value=0,
            key="backtest_spread_pips"
        )
        spread = spread_pips * point

    with col3:
        trade_types = st.multiselect(
            "Направления сделок",
            ["buy", "sell"],
            default=["buy", "sell"],
            key="backtest_trade_types"
        )

    # Запуск бэктеста
    st.subheader("4. Запуск бэктеста")

    if st.button("▶️ Запустить бэктест", type="primary", use_container_width=True):
        if not trade_types:
            st.error("Выберите хотя бы одно направление сделок!")
            return

        with st.spinner("⏳ Выполняется бэктест..."):
            # Убираем служебные поля из стратегии
            strategy = {k: v for k, v in selected_strategy.items() if not k.startswith('_')}

            results = {}

            for trade_type in trade_types:
                try:
                    # Запуск бэктеста
                    backtest = BacktestStrategyProcessor(
                        candles,
                        strategy,
                        trade_type,
                        point,
                        spread
                    )

                    metrics = backtest.process_strategy()

                    results[trade_type] = metrics

                except Exception as e:
                    st.error(f"Ошибка при бэктесте {trade_type}: {e}")
                    import traceback
                    st.code(traceback.format_exc())

        # Показать результаты
        if results:
            st.success("✅ Бэктест завершен!")

            # Сохранить метрики для каждого типа сделки
            for trade_type, metrics in results.items():
                update_strategy_metrics(selected_strategy_name, trade_type, metrics)

            st.success("💾 Метрики сохранены!")

            for trade_type, metrics in results.items():
                st.subheader(f"📊 Результаты для {trade_type.upper()}")

                # Основные метрики в колонках
                col1, col2, col3, col4 = st.columns(4)

                main_metrics = metrics
                additional_metrics = metrics.get('additional_metrics', {})
                if additional_metrics is None:
                    additional_metrics = {}

                with col1:
                    st.metric("Всего сделок", main_metrics.get('full_deals_cnt', 0))
                    st.metric("Прибыльных", main_metrics.get('profit_deals_cnt', 0))

                with col2:
                    st.metric("Убыточных", main_metrics.get('loss_deals_cnt', 0))
                    profit = main_metrics.get('full_deals_saldo', 0)
                    st.metric("Общая прибыль", f"${profit:.2f}")

                with col3:
                    win_rate = additional_metrics.get('win_rate', 0)
                    st.metric("Винрейт", f"{win_rate:.2f}%")
                    max_dd = additional_metrics.get('max_drawdown', 0)
                    st.metric("Макс. просадка", f"${max_dd:.2f}")

                with col4:
                    profit_factor = additional_metrics.get('profit_factor', 0)
                    st.metric("Profit Factor", f"{profit_factor:.2f}")
                    avg_profit = main_metrics.get('prodfit_deals_saldo', 0)
                    st.metric("Средняя прибыль", f"${avg_profit:.2f}")

                # Детальные метрики
                with st.expander("📈 Детальные метрики"):
                    st.json(main_metrics)

                st.divider()


def main():
    """Главная функция приложения"""
    st.title("📈 TraderHub Strategy Constructor")
    st.markdown("---")

    # Sidebar навигация
    with st.sidebar:
        st.header("Навигация")
        page = st.radio(
            "Выберите страницу:",
            ["📝 Создать стратегию", "📚 Список стратегий", "🚀 Бэктест"],
            label_visibility="collapsed"
        )

        st.markdown("---")
        st.markdown("### О конструкторе")
        st.info(
            "Этот конструктор позволяет создавать торговые стратегии "
            "для анализа с помощью библиотеки TraderHub TradeAnalytica."
        )

        st.markdown("### Как использовать:")
        st.markdown(
            """
            1. Создайте стратегию, добавив условия входа
            2. Настройте параметры выхода (SL/TP)
            3. Сохраните стратегию в JSON
            4. Запустите бэктест на исторических данных
            5. Проанализируйте результаты
            """
        )

    # Основной контент
    if page == "📝 Создать стратегию":
        strategy_builder_page()
    elif page == "📚 Список стратегий":
        strategies_list_page()
    elif page == "🚀 Бэктест":
        backtest_page()


if __name__ == "__main__":
    main()
