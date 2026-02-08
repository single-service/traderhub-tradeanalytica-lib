.PHONY: help format lint run_test build test test-all test-condition test-backtest test-prediction clean shell constructor

IMAGE_NAME = tradeanalytica-test
CONTAINER_NAME = tradeanalytica-test-runner

help:
	@echo "Доступные команды:"
	@echo "  make format           - Форматирование кода"
	@echo "  make lint             - Проверка качества кода"
	@echo "  make run_test         - Локальный запуск тестов"
	@echo "  make constructor      - Запустить визуальный конструктор стратегий"
	@echo ""
	@echo "Docker команды:"
	@echo "  make build            - Собрать Docker образ для тестов"
	@echo "  make test             - Запустить все тесты в Docker"
	@echo "  make test-condition   - Запустить тесты ConditionChecker"
	@echo "  make test-backtest    - Запустить тесты BacktestTest"
	@echo "  make test-prediction  - Запустить тесты с предсказаниями"
	@echo "  make test-all         - Запустить все тесты последовательно"
	@echo "  make shell            - Открыть shell в контейнере"
	@echo "  make clean            - Удалить Docker образ и контейнеры"

format:
	black .
	isort .

lint:
	black --check .
	isort --check .
	flake8 --inline-quotes '"'
	pylint $(shell git ls-files '*.py')
	PYTHONPATH=/ mypy --namespace-packages --show-error-codes . --check-untyped-defs --ignore-missing-imports --show-traceback

run_test:
	python3 setup.py sdist bdist_wheel
	pip install dist/traderhub_tradeanalytica-0.0.3-py3-none-any.whl
	python3 -m unittest test_backtest.py

build:
	@echo "Сборка Docker образа..."
	docker build -t $(IMAGE_NAME) .

test: build
	@echo "Запуск всех тестов..."
	docker run --rm $(IMAGE_NAME) pytest -v

test-condition: build
	@echo "Запуск тестов ConditionChecker..."
	docker run --rm $(IMAGE_NAME) pytest test.py::ConditionCheckerTest -v

test-backtest: build
	@echo "Запуск тестов BacktestTest из test.py..."
	docker run --rm $(IMAGE_NAME) pytest test.py::BacktestTest::test_backtest -v

test-backtest-v2: build
	@echo "Запуск тестов BacktestTest из test_backtest.py..."
	docker run --rm $(IMAGE_NAME) pytest test_backtest.py::BacktestTest::test_backtest -v

test-prediction: build
	@echo "Запуск тестов с предсказаниями..."
	docker run --rm $(IMAGE_NAME) pytest test_prediction.py::BacktestPredictionTest::test_prediction_backtest -v

test-all: test-condition test-backtest test-backtest-v2
	@echo "Все тесты завершены!"

shell: build
	@echo "Открытие shell в контейнере..."
	docker run --rm -it $(IMAGE_NAME) /bin/bash

clean:
	@echo "Удаление Docker образа и контейнеров..."
	docker rm -f $(CONTAINER_NAME) 2>/dev/null || true
	docker rmi -f $(IMAGE_NAME) 2>/dev/null || true
	@echo "Очистка завершена!"

constructor:
	@echo "Запуск визуального конструктора стратегий..."
	@echo "Откроется в браузере по адресу http://localhost:8501"
	streamlit run constructor.py
