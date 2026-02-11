#!/usr/bin/env python3
"""
Скрипт для параллельного бэктестинга простых стратегий.
"""

import json
import warnings
import gc
import os
from time import sleep
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
import pandas as pd

from traderhub_tradeanalytica import BacktestStrategyProcessor

# Отключить все warnings
warnings.filterwarnings('ignore')

# Константы
# Оптимальное количество процессов = количество CPU ядер
MAX_PARALLEL_TASKS = min(os.cpu_count() or 4, 8)  # Максимум 8 процессов
MAX_TASKS_PER_CHILD = 100  # Перезапускать процесс после 100 задач (освобождение памяти)

STRATEGIES_DIR = Path("strategies")
METRICS_DIR = Path("metrics")
CANDLES_PATH = "test_data/EURUSD_60_2016-01-01_2024-06-01.csv"

# Параметры бэктеста
POINT = 0.0001
SPREAD = 15 * POINT
TRADE_TYPE = "buy"  # Простые стратегии только для buy

# Глобальная переменная для хранения данных свечей в каждом процессе
_candles = None


def load_candles(candles_path):
    """Загрузка данных свечей."""
    candles = pd.read_csv(
        candles_path,
        names=['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume'],
        index_col=False
    )

    # Создание новой колонки 'Datetime'
    candles['Datetime'] = pd.to_datetime(
        candles['Date'] + ' ' + candles['Time'],
        format='%Y.%m.%d %H:%M'
    )

    # Удаление исходных колонок 'Date' и 'Time'
    candles.drop(columns=['Date', 'Time'], inplace=True)

    # Удаление дубликатов по индексу
    candles = candles[~candles.index.duplicated(keep='first')]

    # Установка колонки 'Datetime' в качестве индекса
    candles.set_index('Datetime', inplace=True)

    return candles


def init_worker(candles_path):
    """
    Инициализация worker-процесса.
    Загружает данные свечей один раз при создании процесса.
    """
    global _candles
    _candles = load_candles(candles_path)
    # Принудительная очистка памяти после загрузки
    gc.collect()


def get_strategy_metrics_path(strategy_filename):
    """Получение пути к файлу метрик для стратегии."""
    return METRICS_DIR / strategy_filename


def strategy_already_processed(strategy_filename):
    """Проверка, обработана ли уже стратегия."""
    metrics_path = get_strategy_metrics_path(strategy_filename)
    return metrics_path.exists()


def save_strategy_metrics(strategy_filename, strategy_metrics):
    """
    Сохранение метрик для одной стратегии в отдельный файл.
    Lock не нужен, так как каждая стратегия пишет в свой уникальный файл.
    """
    # Добавляем метку времени
    strategy_metrics["last_backtest"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Сохраняем в отдельный файл
    metrics_path = get_strategy_metrics_path(strategy_filename)
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(strategy_metrics, f, indent=4, ensure_ascii=False)


def backtest_strategy(strategy_path, candles):
    """
    Выполнение бэктеста для одной стратегии.

    Args:
        strategy_path: Path к файлу стратегии
        candles: DataFrame с данными свечей

    Returns:
        tuple: (strategy_filename, metrics_dict) или (strategy_filename, None) при ошибке
    """
    strategy_filename = strategy_path.name

    try:
        # Загружаем стратегию
        with open(strategy_path, "r", encoding="utf-8") as f:
            strategy = json.load(f)

        # Запускаем бэктест
        backtest_service = BacktestStrategyProcessor(
            candles, strategy, TRADE_TYPE, POINT, SPREAD
        )
        metrics = backtest_service.process_strategy()

        # Формируем результат
        result = {
            TRADE_TYPE: metrics
        }

        # Очищаем временные объекты
        del backtest_service
        gc.collect()

        return strategy_filename, result

    except Exception as e:
        print(f"Ошибка при обработке {strategy_filename}: {e}")
        gc.collect()
        return strategy_filename, None


def backtest_strategy_wrapper(strategy_path):
    """
    Wrapper для передачи в ProcessPoolExecutor.
    Использует глобальную переменную _candles, загруженную в init_worker.
    """
    global _candles
    return backtest_strategy(strategy_path, _candles)


def get_strategies_to_process(strategies_dir):
    """
    Получение списка стратегий для обработки.

    Args:
        strategies_dir: Path к директории со стратегиями

    Returns:
        tuple: (список Path к файлам стратегий для обработки, количество уже обработанных)
    """
    all_strategies = list(strategies_dir.glob("*.json"))
    print(f"Всего стратегий найдено: {len(all_strategies)}")

    strategies_to_process = []
    already_processed = 0

    for strategy_path in all_strategies:
        strategy_filename = strategy_path.name

        # Проверяем, существует ли файл метрик для этой стратегии
        if strategy_already_processed(strategy_filename):
            already_processed += 1
            continue

        strategies_to_process.append(strategy_path)

    print(f"Уже обработано: {already_processed}")
    print(f"Стратегий для обработки: {len(strategies_to_process)}")
    return strategies_to_process, already_processed


def main():
    """Главная функция."""
    print("=" * 60)
    print("Бэктестинг простых стратегий")
    print("=" * 60)

    # Создаем директорию для метрик если её нет
    METRICS_DIR.mkdir(exist_ok=True)

    # Сканирование стратегий
    print("\n1. Сканирование стратегий...")
    strategies_to_process, already_processed = get_strategies_to_process(STRATEGIES_DIR)

    if not strategies_to_process:
        print("\nВсе стратегии уже обработаны!")
        return

    print(f"\n2. Запуск бэктестинга для {len(strategies_to_process)} стратегий...")
    print(f"   Параллельных процессов: {MAX_PARALLEL_TASKS}")
    print(f"   Тип сделок: {TRADE_TYPE}")
    print(f"   Данные свечей будут загружены в каждом процессе при инициализации")
    sleep(3)

    # Счетчики
    processed = 0
    errors = 0
    total = len(strategies_to_process)

    # Для предотвращения утечек памяти обрабатываем стратегии пакетами
    # Перезапуск executor каждые MAX_TASKS_PER_CHILD стратегий
    batch_size = MAX_TASKS_PER_CHILD
    strategies_batches = [
        strategies_to_process[i:i + batch_size]
        for i in range(0, len(strategies_to_process), batch_size)
    ]

    print(f"   Обработка в {len(strategies_batches)} пакетах по {batch_size} стратегий")

    for batch_num, batch in enumerate(strategies_batches, 1):
        print(f"\n   Пакет {batch_num}/{len(strategies_batches)}")

        # Запускаем параллельную обработку для текущего пакета
        # initializer загрузит данные свечей один раз в каждом процессе
        with ProcessPoolExecutor(
            max_workers=MAX_PARALLEL_TASKS,
            initializer=init_worker,
            initargs=(CANDLES_PATH,)
        ) as executor:
            # Запускаем задачи для текущего пакета
            futures = {
                executor.submit(backtest_strategy_wrapper, strategy_path): strategy_path
                for strategy_path in batch
            }

            # Обрабатываем результаты по мере завершения
            for future in as_completed(futures):
                try:
                    strategy_filename, metrics_result = future.result()

                    if metrics_result is not None:
                        # Сохраняем метрики в отдельный файл
                        save_strategy_metrics(strategy_filename, metrics_result)
                        processed += 1

                        if processed % 10 == 0:
                            print(f"      Обработано: {processed}/{total} ({processed/total*100:.1f}%)")
                    else:
                        errors += 1

                except Exception as e:
                    print(f"      Ошибка при обработке задачи: {e}")
                    errors += 1

        # После обработки пакета принудительно очищаем память
        gc.collect()
        print(f"      Пакет завершён, память очищена")

    print(f"\n3. Обработка завершена!")
    print(f"   Успешно обработано: {processed}")
    print(f"   Ошибок: {errors}")
    print(f"   Метрики сохранены в: {METRICS_DIR}/")

    print("\n" + "=" * 60)
    print("Бэктестинг завершен!")
    print("=" * 60)


if __name__ == "__main__":
    main()
