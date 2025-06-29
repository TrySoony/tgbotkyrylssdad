import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import logging
import os
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_ADMIN_ID, ENABLE_TRADING, DEMO_MODE
from trader import AggressiveFuturesTrader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tg_bot")

bot = Bot(
    token=TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

trader = AggressiveFuturesTrader()
trading_task = None

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
    status = "🟢 ВКЛЮЧЕНА" if trader.is_running() else "🔴 ОТКЛЮЧЕНА"
    await message.answer(f"<b>Статус торговли:</b> {status}\n<b>Демо-режим:</b> {'🟢' if trader.current_balance == trader.initial_balance or DEMO_MODE else '🔴'}")

@dp.message(Command("enable"))
async def cmd_enable(message: types.Message):
    global trading_task
    if message.from_user.id != TELEGRAM_ADMIN_ID:
        await message.answer("⛔️ Нет доступа")
        return
    if trader.is_running():
        await message.answer("Торговля уже запущена!")
        return
    trading_task = asyncio.create_task(trader.run_trading_cycle())
    await message.answer("✅ Торговля <b>ВКЛЮЧЕНА</b>")

@dp.message(Command("disable"))
async def cmd_disable(message: types.Message):
    if message.from_user.id != TELEGRAM_ADMIN_ID:
        await message.answer("⛔️ Нет доступа")
        return
    if not trader.is_running():
        await message.answer("Торговля уже остановлена!")
        return
    trader.stop()
    await message.answer("⛔️ Торговля <b>ОТКЛЮЧЕНА</b>")

@dp.message(Command("positions"))
async def cmd_positions(message: types.Message):
    if message.from_user.id != TELEGRAM_ADMIN_ID:
        await message.answer("⛔️ Нет доступа")
        return
    positions = [f"{s}: {p}" for s, p in trader.current_positions.items() if p]
    if not positions:
        await message.answer("Нет открытых позиций.")
        return
    await message.answer("<b>Открытые позиции:</b>\n" + "\n".join(positions))

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
    # Переключаем режим в config.py
    import config
    import importlib
    importlib.reload(config)
    # Читаем и меняем строки
    with open('config.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    new_lines = []
    new_enable = None
    new_demo = None
    for line in lines:
        if line.strip().startswith('ENABLE_TRADING'):
            if 'True' in line:
                new_lines.append('ENABLE_TRADING = False  # Отключено через Telegram\n')
                new_enable = False
            else:
                new_lines.append('ENABLE_TRADING = True  # Включено через Telegram\n')
                new_enable = True
        elif line.strip().startswith('DEMO_MODE'):
            if 'True' in line:
                new_lines.append('DEMO_MODE = False  # Отключено через Telegram\n')
                new_demo = False
            else:
                new_lines.append('DEMO_MODE = True  # Включено через Telegram\n')
                new_demo = True
        else:
            new_lines.append(line)
    with open('config.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    importlib.reload(config)
    if new_enable and not new_demo:
        await message.answer('⚡️ Переключено на <b>РЕАЛЬНУЮ ТОРГОВЛЮ</b>! Будьте осторожны!')
    else:
        await message.answer('🟢 Переключено на <b>ДЕМО-РЕЖИМ</b>.')

# --- Запуск ---
async def main():
    logger.info("Запуск Telegram-бота...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 