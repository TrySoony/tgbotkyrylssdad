# Конфигурация для агрессивной торговли фьючерсами Bybit
# ВНИМАНИЕ: Это высокорискованная стратегия для разгона депозита

# API ключи Bybit (замените на свои)
API_KEY = "LdfcJrBATjtIjsHNYj"
API_SECRET = "1OeWgfvSOJVacF5iWS77Dt4HwkfKlcDNf4es"

# Выбор биржи ('bybit' или 'binance')
EXCHANGE = "bybit"

# Настройки торговли
ENABLE_TRADING = False  # Установите True для включения реальной торговли
# SYMBOLS = ["BTC/USDT", "ETH/USDT", ...]  # Можно указать список пар вручную
SYMBOLS = None  # None = автоопределение всех USDT-пар
LEVERAGE = 50  # Плечо (x20-x100)
POSITION_SIZE_PERCENT = 95  # Процент депозита для каждой сделки (90-95%)

# Параметры стратегии
TIMEFRAME = "1m"  # Таймфрейм для анализа
CANDLE_BODY_THRESHOLD = 0.5  # Минимальный размер тела свечи в %
VOLUME_PERIOD = 10  # Период для расчета среднего объема
TAKE_PROFIT_PERCENT = 5.0  # Тейк-профит в %
STOP_LOSS_PERCENT = 2.0  # Стоп-лосс в %

# Настройки логирования
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# Настройки безопасности
MAX_DAILY_TRADES = 50  # Максимальное количество сделок в день
MAX_DAILY_LOSS = 15  # Максимальный дневной убыток в %
EMERGENCY_STOP_LOSS = 20  # Экстренный стоп-лосс в %

# Тестовые настройки (для демо-режима)
DEMO_MODE = True  # True для тестирования без реальных сделок
INITIAL_BALANCE = 80  # Начальный баланс в USD
TARGET_BALANCE = 400  # Целевой баланс в USD

# Настройки Telegram-бота
TELEGRAM_BOT_TOKEN = "7524709955:AAGokRF2gy0gNvswsrU7I2imkLNMGScBI7c"
TELEGRAM_ADMIN_ID = 5058443853  # Ваш Telegram user ID (int) 