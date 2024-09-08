# traderhub_tradeanalytica

`traderhub_tradeanalytica` — это библиотека Python для тестирования торговых стратегий на исторических данных и анализа рыночных условий.

## Основные возможности

- **BacktestStrategyProcessor**: Проверка стратегий на исторических данных.
- **ConditionChecker**: Проверка условий торговых стратегий.
- **CONDITIONS_GROUPS и GROUP_MODELS_MAP**: Справочники групп инструментов, используемых в стратегиях (индикаторы, свечи, свечные паттерны, геометрические паттерны).

## Установка

Вы можете установить библиотеку с помощью pip:

```bash
pip install traderhub_tradeanalytica
```

# Использование
1. Проверка стратегий на исторических данных
Для использования BacktestStrategyProcessor:

```python
from traderhub_tradeanalytica import BacktestStrategyProcessor

# Инициализация процессора для тестирования стратегии
processor = BacktestStrategyProcessor(data, strategy, trend_type)
processor.process_strategy()
```
data — исторические данные (например, OHLCV).
strategy — торговая стратегия, содержащая условия для входа и выхода.
trend_type — тип тренда (например, "buy" или "sell").

2. Проверка условий по стратегиям
Для использования ConditionChecker:

```python
from traderhub_tradeanalytica import ConditionChecker

# Инициализация чекера для проверки условий
checker = ConditionChecker(current_candle, candles, ask, bid, point)

# Пример вызова метода для проверки условия
result = checker.check_condition(...)
```
current_candle — текущая свеча.
candles — массив предыдущих свечей.
ask и bid — текущие значения спроса и предложения.
point — минимальное изменение цены (тик).
3. Справочники групп инструментов для стратегий
Для использования справочников:

```python
from traderhub_tradeanalytica import CONDITIONS_GROUPS, GROUP_MODELS_MAP

# Получение справочников групп инструментов
print(CONDITIONS_GROUPS)
print(GROUP_MODELS_MAP)
```
CONDITIONS_GROUPS: Содержит информацию о доступных группах инструментов (индикаторы, свечи, свечные паттерны, геометрические паттерны).
GROUP_MODELS_MAP: Маппинг моделей для каждой группы инструментов.

# Зависимости
Библиотека использует следующие зависимости:

requests>=2.25.1
pandas>=2.2.2
TA-Lib-Precompiled>=0.4.25
numpy>=1.24.2,<1.26.0
pandas_ta>=0.3.14b
sortedcontainers

# Вклад
Мы приветствуем вклад сообщества в развитие библиотеки! Пожалуйста, создавайте issues и pull requests в этом репозитории.

# Лицензия
Эта библиотека распространяется под MIT License.