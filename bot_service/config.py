# Конфигурация для торгового и Telegram-бота

# API ключи Bybit (замени на свои)
API_KEY = "LdfcJrBATjtIjsHNYj"
API_SECRET = "1OeWgfvSOJVacF5iWS77Dt4HwkfKlcDNf4es"

# Настройки торговли
ENABLE_TRADING = True  # По умолчанию торговля выключена
DEMO_MODE = False       # По умолчанию демо-режим
SYMBOLS = None          # None = автоопределение всех USDT-пар
LEVERAGE = 50
POSITION_SIZE_PERCENT = 95
TIMEFRAME = "1m"
CANDLE_BODY_THRESHOLD = 0.5
VOLUME_PERIOD = 10
TAKE_PROFIT_PERCENT = 5.0
STOP_LOSS_PERCENT = 2.0
MAX_DAILY_TRADES = 50
MAX_DAILY_LOSS = 15
EMERGENCY_STOP_LOSS = 20
INITIAL_BALANCE = 80
TARGET_BALANCE = 400

# Логирование
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# Telegram-бот
TELEGRAM_BOT_TOKEN = "7524709955:AAGokRF2gy0gNvswsrU7I2imkLNMGScBI7c"
TELEGRAM_ADMIN_ID = 5058443853  # Замени на свой Telegram ID 