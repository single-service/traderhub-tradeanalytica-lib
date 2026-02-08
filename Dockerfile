FROM python:3.10-slim

WORKDIR /app

# Установка системных зависимостей для TA-Lib
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Установка TA-Lib
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && \
    rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# Копирование только requirements.txt сначала для кеширования
COPY requirements.txt /app/

# Установка Python зависимостей (без TA-Lib-Precompiled)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir numpy>=2.0.0 && \
    pip install --no-cache-dir pandas>=2.2.2 && \
    pip install --no-cache-dir TA-Lib && \
    pip install --no-cache-dir pandas-ta-classic>=0.3.59 && \
    pip install --no-cache-dir sortedcontainers>=2.4.0 && \
    pip install --no-cache-dir requests>=2.32.5 && \
    pip install --no-cache-dir pytest>=7.0.0

# Копирование остальных файлов проекта
COPY . /app/

# Установка проекта в режиме разработки
RUN pip install --no-cache-dir -e .

# Команда по умолчанию
CMD ["pytest", "-v"]
