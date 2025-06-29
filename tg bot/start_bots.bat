@echo off
echo 🚀 Запуск торгового бота и Telegram-бота
echo.

echo 📦 Установка зависимостей...
pip install -r requirements.txt
cd "trading bot"
pip install -r requirements.txt
cd ..

echo.
echo 🤖 Запуск Telegram-бота в фоновом режиме...
start "Telegram Bot" cmd /k "cd /d %~dp0 && python tg_bot.py"

echo.
echo 📈 Запуск торгового бота...
cd "trading bot"
python main.py

pause 