#!/bin/bash

echo "🚀 Запуск торгового бота и Telegram-бота"
echo

echo "📦 Установка зависимостей..."
pip3 install -r requirements.txt
cd "trading bot"
pip3 install -r requirements.txt
cd ..

echo
echo "🤖 Запуск Telegram-бота в фоновом режиме..."
nohup python3 tg_bot.py > telegram_bot.log 2>&1 &
TELEGRAM_PID=$!
echo "Telegram-бот запущен с PID: $TELEGRAM_PID"

echo
echo "📈 Запуск торгового бота..."
cd "trading bot"
python3 main.py

# Остановка Telegram-бота при завершении
echo "🛑 Остановка Telegram-бота..."
kill $TELEGRAM_PID 