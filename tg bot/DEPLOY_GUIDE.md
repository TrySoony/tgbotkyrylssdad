# 🚀 Руководство по деплою торгового бота

## 📋 Предварительные требования

### 1. Подготовка API ключей
- **Bybit**: Создайте API ключи на [Bybit](https://www.bybit.com)
- **Telegram**: Получите токен бота у [@BotFather](https://t.me/BotFather)

### 2. Системные требования
- Python 3.8+
- Стабильное интернет-соединение
- Сервер/компьютер с 24/7 доступом

## 🔧 Шаг 1: Настройка окружения

### Установка Python и зависимостей

```bash
# Установка Python (если не установлен)
# Windows: скачайте с python.org
# Linux: sudo apt install python3 python3-pip

# Переход в папку проекта
cd "tg bot"

# Установка зависимостей для Telegram-бота
pip install -r requirements.txt

# Переход в папку торгового бота
cd "../trading bot"

# Установка зависимостей для торгового бота
pip install -r requirements.txt
```

### Проверка зависимостей
Оба проекта используют одинаковые зависимости:
- `ccxt>=4.0.0` - для работы с биржами
- `python-dateutil>=2.8.0` - для работы с датами
- `aiogram>=3.0.0` - для Telegram-бота

## 🔑 Шаг 2: Настройка API ключей

### 1. Получение API ключей Bybit
1. Зайдите на [Bybit](https://www.bybit.com)
2. Перейдите в API Management
3. Создайте новый API ключ
4. Включите права на торговлю фьючерсами
5. Скопируйте `API Key` и `Secret Key`

### 2. Получение токена Telegram-бота
1. Напишите [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте полученный токен

### 3. Получение вашего Telegram ID
1. Напишите [@userinfobot](https://t.me/userinfobot) в Telegram
2. Скопируйте ваш `ID`

### 4. Обновление конфигурации
Откройте файл `config.py` в обеих папках и замените:

```python
# API ключи Bybit (замените на свои)
API_KEY = "ваш_api_ключ_bybit"
API_SECRET = "ваш_секретный_ключ_bybit"

# Настройки Telegram-бота
TELEGRAM_BOT_TOKEN = "ваш_токен_бота"
TELEGRAM_ADMIN_ID = ваш_telegram_id  # без кавычек
```

## 🚀 Шаг 3: Запуск проектов

### Вариант 1: Локальный запуск (для тестирования)

#### Запуск торгового бота:
```bash
cd "trading bot"
python main.py
```

#### Запуск Telegram-бота (в отдельном терминале):
```bash
cd "tg bot"
python tg_bot.py
```

### Вариант 2: Запуск на сервере (рекомендуется)

#### Использование screen (Linux):
```bash
# Установка screen
sudo apt install screen

# Запуск торгового бота
screen -S trading_bot
cd "trading bot"
python main.py
# Ctrl+A, затем D для отключения

# Запуск Telegram-бота
screen -S telegram_bot
cd "tg bot"
python tg_bot.py
# Ctrl+A, затем D для отключения

# Просмотр сессий
screen -ls

# Подключение к сессии
screen -r trading_bot
screen -r telegram_bot
```

#### Использование systemd (Linux):
Создайте файлы сервисов:

**/etc/systemd/system/trading-bot.service:**
```ini
[Unit]
Description=Trading Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/trading bot
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**/etc/systemd/system/telegram-bot.service:**
```ini
[Unit]
Description=Telegram Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/tg bot
ExecStart=/usr/bin/python3 tg_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Запуск сервисов:
```bash
sudo systemctl enable trading-bot
sudo systemctl start trading-bot
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot

# Проверка статуса
sudo systemctl status trading-bot
sudo systemctl status telegram-bot
```

## 🔒 Шаг 4: Настройка безопасности

### 1. Переключение в реальный режим
В файле `config.py` измените:
```python
ENABLE_TRADING = True  # Включить реальную торговлю
DEMO_MODE = False      # Отключить демо-режим
```

### 2. Проверка настроек
- Убедитесь, что API ключи правильные
- Проверьте баланс на Bybit
- Убедитесь, что у ключей есть права на торговлю фьючерсами

## 📱 Шаг 5: Использование Telegram-бота

### Доступные команды:
- `/start` - информация о боте
- `/status` - статус торговли
- `/enable` - включить торговлю
- `/disable` - выключить торговлю
- `/positions` - открытые позиции
- `/logs` - последние логи
- `/switch` - переключить режим (демо/реальная торговля)

### Пример использования:
1. Найдите вашего бота в Telegram
2. Отправьте `/start`
3. Используйте команды для управления

## ⚠️ Важные предупреждения

### 1. Риски
- Это высокорискованная стратегия
- Возможна полная потеря депозита
- Используйте только те деньги, которые готовы потерять

### 2. Мониторинг
- Регулярно проверяйте логи
- Следите за балансом
- Используйте Telegram-бота для контроля

### 3. Безопасность
- Не делитесь API ключами
- Используйте надежный сервер
- Регулярно обновляйте зависимости

## 🔧 Устранение неполадок

### Проблемы с подключением к Bybit:
```bash
# Проверка интернет-соединения
ping api.bybit.com

# Проверка API ключей
python -c "import ccxt; print(ccxt.bybit().fetch_balance())"
```

### Проблемы с Telegram-ботом:
```bash
# Проверка токена
curl "https://api.telegram.org/botВАШ_ТОКЕН/getMe"
```

### Проблемы с зависимостями:
```bash
# Обновление pip
pip install --upgrade pip

# Переустановка зависимостей
pip uninstall ccxt aiogram python-dateutil
pip install -r requirements.txt
```

## 📊 Мониторинг работы

### Логи торгового бота:
- Файл `trading.log` в папке торгового бота
- Консольный вывод при запуске

### Логи Telegram-бота:
- Консольный вывод при запуске
- Сообщения в Telegram

### Полезные команды для мониторинга:
```bash
# Просмотр логов в реальном времени
tail -f trading.log

# Проверка процессов
ps aux | grep python

# Проверка использования памяти
htop
```

## 🎯 Готово!

После выполнения всех шагов у вас будет:
- ✅ Работающий торговый бот с балансом $80 → $400
- ✅ Telegram-бот для удаленного управления
- ✅ Автоматический перезапуск при сбоях
- ✅ Логирование всех операций

**Удачи в торговле! 🚀** 