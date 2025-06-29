import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
import logging
import os
import sys
import importlib
from aiogram.client.default import DefaultBotProperties

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_ADMIN_ID
import config

# Для получения информации о торговле
from main import AggressiveFuturesTrader

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(
    token=TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Глобальный объект трейдера (можно заменить на singleton или manager)
trader: AggressiveFuturesTrader = None

# --- Вспомогательные функции ---
def reload_config():
    importlib.reload(config)

def set_enable_trading(value: bool):
    # Меняем флаг в config.py (и в памяти)
    with open('config.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    with open('config.py', 'w', encoding='utf-8') as f:
        for line in lines:
            if line.strip().startswith('ENABLE_TRADING'):
                f.write(f'ENABLE_TRADING = {str(value)}  # Установлено через Telegram\n')
            else:
                f.write(line)
    reload_config()
    logger.info(f"ENABLE_TRADING изменён на {value} через Telegram")

def set_demo_mode(value: bool):
    # Меняем флаг DEMO_MODE в config.py (и в памяти)
    with open('config.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    with open('config.py', 'w', encoding='utf-8') as f:
        for line in lines:
            if line.strip().startswith('DEMO_MODE'):
                f.write(f'DEMO_MODE = {str(value)}  # Установлено через Telegram\n')
            else:
                f.write(line)
    reload_config()
    logger.info(f"DEMO_MODE изменён на {value} через Telegram")

# --- Команды ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.from_user.id != TELEGRAM_ADMIN_ID:
        await message.answer("⛔️ Нет доступа")
        return
    await message.answer("<b>🤖 Агрессивный трейдинг-бот</b>\n\nДоступные команды:\n/status — статус\n/enable — включить торговлю\n/disable — выключить торговлю\n/positions — открытые позиции\n/logs — последние логи\n/switch — переключить режим")

@dp.message(Command("status"))
async def cmd_status(message: types.Message):
    if message.from_user.id != TELEGRAM_ADMIN_ID:
        await message.answer("⛔️ Нет доступа")
        return
    reload_config()
    status = "🟢 ВКЛЮЧЕНА" if config.ENABLE_TRADING else "🔴 ОТКЛЮЧЕНА"
    await message.answer(f"<b>Статус торговли:</b> {status}\n\n<b>Демо-режим:</b> {'🟢' if config.DEMO_MODE else '🔴'}")

@dp.message(Command("enable"))
async def cmd_enable(message: types.Message):
    if message.from_user.id != TELEGRAM_ADMIN_ID:
        await message.answer("⛔️ Нет доступа")
        return
    set_enable_trading(True)
    await message.answer("✅ Торговля <b>ВКЛЮЧЕНА</b>")

@dp.message(Command("disable"))
async def cmd_disable(message: types.Message):
    if message.from_user.id != TELEGRAM_ADMIN_ID:
        await message.answer("⛔️ Нет доступа")
        return
    set_enable_trading(False)
    await message.answer("⛔️ Торговля <b>ОТКЛЮЧЕНА</b>")

@dp.message(Command("positions"))
async def cmd_positions(message: types.Message):
    if message.from_user.id != TELEGRAM_ADMIN_ID:
        await message.answer("⛔️ Нет доступа")
        return
    # Для простоты: читаем из trading.log последние открытые позиции
    if not os.path.exists('trading.log'):
        await message.answer("Нет данных о позициях.")
        return
    with open('trading.log', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    positions = [l for l in lines if 'ПОЗИЦИЯ ОТКРЫТА' in l]
    if not positions:
        await message.answer("Нет открытых позиций.")
        return
    await message.answer("<b>Последние открытые позиции:</b>\n" + ''.join(positions[-5:]), parse_mode=ParseMode.HTML)

@dp.message(Command("logs"))
async def cmd_logs(message: types.Message):
    if message.from_user.id != TELEGRAM_ADMIN_ID:
        await message.answer("⛔️ Нет доступа")
        return
    if not os.path.exists('trading.log'):
        await message.answer("Нет логов.")
        return
    with open('trading.log', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    await message.answer("<b>Последние логи:</b>\n<pre>" + ''.join(lines[-20:]) + "</pre>", parse_mode=ParseMode.HTML)

@dp.message(Command("switch"))
async def cmd_switch(message: types.Message):
    if message.from_user.id != TELEGRAM_ADMIN_ID:
        await message.answer("⛔️ Нет доступа")
        return
    reload_config()
    if config.DEMO_MODE:
        set_demo_mode(False)
        await message.answer("⚡️ Переключено на <b>РЕАЛЬНУЮ ТОРГОВЛЮ</b>! Будьте осторожны!")
    else:
        set_demo_mode(True)
        await message.answer("🟢 Переключено на <b>ДЕМО-РЕЖИМ</b>.")

# --- Запуск ---
async def main():
    logger.info("Запуск Telegram-бота...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 