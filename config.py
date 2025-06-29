# Конфигурация для торгового и Telegram-бота

# API ключи Bybit (замени на свои)
API_KEY = "LdfcJrBATjtIjsHNYj"
API_SECRET = "1OeWgfvSOJVacF5iWS77Dt4HwkfKlcDNf4es"

# Настройки торговли
ENABLE_TRADING = True  # По умолчанию торговля выключена
DEMO_MODE = False       # По умолчанию демо-режим
SYMBOLS = [
    "HUSDT/USDT",
    "SKATEUSDT/USDT",
    "SOSUSDT/USDT",
    "CUDIUSDT/USDT",
    "HOMEUSDT/USDT",
    "NEWTUSDT/USDT",
    "SAHARAUSDT/USDT",
    "SPKUSDT/USDT",
    "SQUSDT/USDT",
    "BDXNUSDT/USDT",
    "LAUSDT/USDT",
    "B2USDT/USDT",
    "RESOLVUSDT/USDT"
]
LEVERAGE = 50
POSITION_SIZE_PERCENT = 100
TIMEFRAME = "1m"
CANDLE_BODY_THRESHOLD = 0.2
VOLUME_PERIOD = 2
TAKE_PROFIT_PERCENT = 20.0
STOP_LOSS_PERCENT = 2.0
MA_LENGTH = 50
USE_TREND = True
TRADE_LONG = True
TRADE_SHORT = True
MAX_DAILY_TRADES = 1000
MAX_DAILY_LOSS = 50
EMERGENCY_STOP_LOSS = 80
INITIAL_BALANCE = 50
TARGET_BALANCE = 300

# Логирование
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# Telegram-бот
TELEGRAM_BOT_TOKEN = "7524709955:AAGokRF2gy0gNvswsrU7I2imkLNMGScBI7c"
TELEGRAM_ADMIN_ID = 5058443853  # Замени на свой Telegram ID 