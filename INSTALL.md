# Инструкция по установке

## Установка для разработки

### Вариант 1: Использование Docker (рекомендуется)

```bash
# Собрать образ и запустить тесты
make build
make test
```

### Вариант 2: Локальная установка

#### Требования
- Python 3.10+
- TA-Lib C библиотека

#### Установка TA-Lib на разных ОС

**Ubuntu/Debian:**
```bash
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
cd ..
rm -rf ta-lib ta-lib-0.4.0-src.tar.gz
```

**macOS:**
```bash
brew install ta-lib
```

**Windows:**
Скачайте и установите предварительно скомпилированную версию с: https://github.com/TA-Lib/ta-lib-python

#### Установка Python зависимостей

```bash
# Установка зависимостей
pip install numpy>=2.0.0
pip install pandas>=2.2.2
pip install TA-Lib  # Python wrapper для TA-Lib
pip install pandas-ta-classic
pip install sortedcontainers
pip install pytest

# Установка проекта в режиме разработки
pip install -e .
```

## Запуск тестов

```bash
# С использованием Docker
make test-all

# Локально
pytest -v
```

## Известные проблемы

### Ошибка: "numpy.dtype size changed"
Эта ошибка возникает при несовместимости версий numpy и TA-Lib. Решение:
1. Убедитесь, что используете numpy>=2.0.0
2. Установите TA-Lib Python wrapper ПОСЛЕ установки numpy
3. Или используйте Docker (рекомендуется)

### Ошибка при импорте pandas_ta
Убедитесь, что установлен пакет `pandas-ta-classic`, а не `pandas-ta`:
```bash
pip install pandas-ta-classic>=0.3.59
```
