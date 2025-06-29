import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import logging
import os
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_ADMIN_ID, ENABLE_TRADING, DEMO_MODE
from trader import AggressiveFuturesTrader
from aiogram.client.default import DefaultBotProperties
from datetime import datetime
from notifications import send_trade_notification

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tg_bot")

bot = Bot(
    token=TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

trader = AggressiveFuturesTrader()
trading_task = None

# Создание клавиатур
def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Статус", callback_data="status"),
            InlineKeyboardButton(text="🚀 Запустить", callback_data="enable")
        ],
        [
            InlineKeyboardButton(text="⛔️ Остановить", callback_data="disable"),
            InlineKeyboardButton(text="📈 Позиции", callback_data="positions")
        ],
        [
            InlineKeyboardButton(text="📋 Логи", callback_data="logs"),
            InlineKeyboardButton(text="🔄 Переключить режим", callback_data="switch")
        ],
        [
            InlineKeyboardButton(text="💰 Баланс", callback_data="balance"),
            InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")
        ]
    ])
    return keyboard

def get_balance_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💳 Проверить баланс", callback_data="check_balance"),
            InlineKeyboardButton(text="💵 Установить сумму", callback_data="set_amount")
        ],
        [
            InlineKeyboardButton(text="📊 Текущие настройки", callback_data="current_settings"),
            InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")
        ]
    ])
    return keyboard

def get_positions_keyboard():
    """Создаёт клавиатуру для управления открытыми позициями."""
    keyboard = []
    
    # Получаем открытые позиции
    open_positions = [symbol for symbol, pos in trader.current_positions.items() if pos]
    
    if not open_positions:
        keyboard.append([InlineKeyboardButton(text="Нет открытых позиций", callback_data="no_positions")])
    else:
        for symbol in open_positions:
            position = trader.current_positions[symbol]
            # Создаём кнопки для каждой позиции
            keyboard.append([
                InlineKeyboardButton(
                    text=f"📈 {symbol} ({position['direction'].upper()})", 
                    callback_data=f"pos_info_{symbol}"
                )
            ])
            keyboard.append([
                InlineKeyboardButton(
                    text=f"➕ Увеличить {symbol}", 
                    callback_data=f"increase_{symbol}"
                ),
                InlineKeyboardButton(
                    text=f"❌ Закрыть {symbol}", 
                    callback_data=f"close_{symbol}"
                )
            ])
    
    keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# --- Команды ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.from_user.id != TELEGRAM_ADMIN_ID:
        await message.answer("⛔️ Нет доступа")
        return
    await message.answer(
        "<b>🤖 Агрессивный трейдинг-бот</b>\n\nВыберите действие:",
        reply_markup=get_main_keyboard()
    )

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

@dp.message(Command("debug"))
async def cmd_debug(message: types.Message):
    if message.from_user.id != TELEGRAM_ADMIN_ID:
        await message.answer("⛔️ Нет доступа")
        return
    import config
    debug_info = f"""
<b>🔍 ДИАГНОСТИКА БОТА</b>

<b>Статус торговли:</b> {'🟢 ВКЛЮЧЕНА' if trader.is_running() else '🔴 ОТКЛЮЧЕНА'}
<b>Демо-режим:</b> {'🟢 ВКЛЮЧЕН' if config.DEMO_MODE else '🔴 ОТКЛЮЧЕН'}
<b>Реальная торговля:</b> {'🟢 ВКЛЮЧЕНА' if config.ENABLE_TRADING else '🔴 ОТКЛЮЧЕНА'}

<b>Параметры стратегии:</b>
• Тело свечи: {config.CANDLE_BODY_THRESHOLD}%
• Период объема: {config.VOLUME_PERIOD}
• Тейк-профит: {config.TAKE_PROFIT_PERCENT}%
• Стоп-лосс: {config.STOP_LOSS_PERCENT}%

<b>Баланс:</b> ${trader.get_balance():.2f}
<b>Цель:</b> ${config.TARGET_BALANCE}

<b>Позиции:</b> {len([p for p in trader.current_positions.values() if p])}
<b>Сделки за день:</b> {trader.daily_trades}
"""
    await message.answer(debug_info)

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

# --- Callback обработчики ---
@dp.callback_query()
async def handle_callback(callback: CallbackQuery):
    if callback.from_user.id != TELEGRAM_ADMIN_ID:
        await callback.answer("⛔️ Нет доступа")
        return
    
    if callback.data == "main_menu":
        await callback.message.edit_text(
            "<b>🤖 Агрессивный трейдинг-бот</b>\n\nВыберите действие:",
            reply_markup=get_main_keyboard()
        )
    
    elif callback.data == "status":
        status = "🟢 ВКЛЮЧЕНА" if trader.is_running() else "🔴 ОТКЛЮЧЕНА"
        await callback.message.edit_text(
            f"<b>Статус торговли:</b> {status}\n<b>Демо-режим:</b> {'🟢' if trader.current_balance == trader.initial_balance or DEMO_MODE else '🔴'}",
            reply_markup=get_main_keyboard()
        )
    
    elif callback.data == "enable":
        global trading_task
        if trader.is_running():
            await callback.answer("Торговля уже запущена!")
            return
        trading_task = asyncio.create_task(trader.run_trading_cycle())
        await callback.message.edit_text(
            "✅ Торговля <b>ВКЛЮЧЕНА</b>",
            reply_markup=get_main_keyboard()
        )
    
    elif callback.data == "disable":
        if not trader.is_running():
            await callback.answer("Торговля уже остановлена!")
            return
        trader.stop()
        await callback.message.edit_text(
            "⛔️ Торговля <b>ОТКЛЮЧЕНА</b>",
            reply_markup=get_main_keyboard()
        )
    
    elif callback.data == "positions":
        positions = [f"{s}: {p}" for s, p in trader.current_positions.items() if p]
        if not positions:
            await callback.message.edit_text(
                "Нет открытых позиций.",
                reply_markup=get_main_keyboard()
            )
        else:
            await callback.message.edit_text(
                "<b>Открытые позиции:</b>\n" + "\n".join(positions),
                reply_markup=get_positions_keyboard()
            )
    
    elif callback.data.startswith("pos_info_"):
        symbol = callback.data.replace("pos_info_", "")
        if symbol in trader.current_positions and trader.current_positions[symbol]:
            position = trader.current_positions[symbol]
            current_price = trader.get_current_price(symbol)
            pnl = trader.strategies[symbol].calculate_pnl(position, current_price)
            
            info_text = f"""
<b>📊 Информация о позиции</b>

<b>Пара:</b> {symbol}
<b>Направление:</b> {position['direction'].upper()}
<b>Объём:</b> {position['size']:.4f}
<b>Цена входа:</b> {position['entry_price']:.4f}
<b>Текущая цена:</b> {current_price:.4f}
<b>Take Profit:</b> {position['take_profit']:.4f}
<b>Stop Loss:</b> {position['stop_loss']:.4f}
<b>P&L:</b> {pnl:.2f} USDT
<b>Время входа:</b> {position['entry_time'].strftime('%H:%M:%S')}
"""
            await callback.message.edit_text(
                info_text,
                reply_markup=get_positions_keyboard()
            )
    
    elif callback.data.startswith("increase_"):
        symbol = callback.data.replace("increase_", "")
        if symbol in trader.current_positions and trader.current_positions[symbol]:
            # Увеличиваем позицию на 50% от текущего размера
            position = trader.current_positions[symbol]
            current_price = trader.get_current_price(symbol)
            additional_size = position['size'] * 0.5  # Увеличиваем на 50%
            
            if trader.open_position(symbol, position['direction'], current_price, additional_size):
                # Обновляем размер позиции
                trader.current_positions[symbol]['size'] += additional_size
                await callback.answer(f"✅ Позиция {symbol} увеличена на {additional_size:.4f}")
            else:
                await callback.answer(f"❌ Ошибка увеличения позиции {symbol}", show_alert=True)
        else:
            await callback.answer("❌ Позиция не найдена", show_alert=True)
    
    elif callback.data.startswith("close_"):
        symbol = callback.data.replace("close_", "")
        if symbol in trader.current_positions and trader.current_positions[symbol]:
            position = trader.current_positions[symbol]
            current_price = trader.get_current_price(symbol)
            
            if trader.close_position(symbol, position['direction'], position['size']):
                pnl = trader.strategies[symbol].calculate_pnl(position, current_price)
                if DEMO_MODE:
                    trader.current_balance += pnl
                trader.strategies[symbol].log_position_closed(position, current_price, "manual_close", pnl)
                trader.update_daily_stats(pnl)
                
                # Отправляем уведомление о закрытии
                msg = (
                    f"<b>ЗАКРЫТА ПОЗИЦИЯ (РУЧНОЕ ЗАКРЫТИЕ)</b>\n"
                    f"Пара: <b>{symbol}</b>\n"
                    f"Направление: <b>{position['direction'].upper()}</b>\n"
                    f"Объём: <b>{position['size']:.4f}</b>\n"
                    f"Вход: <b>{position['entry_price']:.4f}</b>\n"
                    f"Выход: <b>{current_price:.4f}</b>\n"
                    f"Причина: <b>Ручное закрытие</b>\n"
                    f"PnL: <b>{pnl:.2f} USDT</b>\n"
                )
                await send_trade_notification(msg)
                
                trader.current_positions[symbol] = None
                await callback.answer(f"✅ Позиция {symbol} закрыта. PnL: {pnl:.2f} USDT")
            else:
                await callback.answer(f"❌ Ошибка закрытия позиции {symbol}", show_alert=True)
        else:
            await callback.answer("❌ Позиция не найдена", show_alert=True)
    
    elif callback.data == "no_positions":
        await callback.answer("Нет открытых позиций для управления", show_alert=True)
    
    elif callback.data == "logs":
        if not os.path.exists('trading.log'):
            await callback.message.edit_text(
                "Нет логов.",
                reply_markup=get_main_keyboard()
            )
        else:
            with open('trading.log', 'r', encoding='utf-8') as f:
                lines = f.readlines()
            await callback.message.edit_text(
                "<b>Последние логи:</b>\n<pre>" + ''.join(lines[-20:]) + "</pre>",
                reply_markup=get_main_keyboard()
            )
    
    elif callback.data == "balance":
        await callback.message.edit_text(
            "<b>💰 Управление балансом</b>\n\nВыберите действие:",
            reply_markup=get_balance_keyboard()
        )
    
    elif callback.data == "check_balance":
        try:
            balance = trader.get_balance()
            await callback.answer(f"💳 Доступный баланс: ${balance:.2f}\n<i>{datetime.now().strftime('%H:%M:%S')}</i>", show_alert=True)
        except Exception as e:
            await callback.answer(f"❌ Ошибка получения баланса: {e}", show_alert=True)
    
    elif callback.data == "set_amount":
        await callback.message.edit_text(
            "<b>💵 Установка суммы для работы</b>\n\nОтправьте сумму в USD (например: 100)",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="balance")]
            ])
        )
    
    elif callback.data == "current_settings":
        import config
        settings_info = f"""
<b>⚙️ Текущие настройки</b>

<b>Баланс:</b> ${trader.get_balance():.2f}
<b>Начальный баланс:</b> ${config.INITIAL_BALANCE}
<b>Целевой баланс:</b> ${config.TARGET_BALANCE}
<b>Размер позиции:</b> {config.POSITION_SIZE_PERCENT}%
<b>Плечо:</b> x{config.LEVERAGE}

<b>Стратегия:</b>
• Тейк-профит: {config.TAKE_PROFIT_PERCENT}%
• Стоп-лосс: {config.STOP_LOSS_PERCENT}%
• Тело свечи: {config.CANDLE_BODY_THRESHOLD}%
"""
        await callback.message.edit_text(
            settings_info,
            reply_markup=get_balance_keyboard()
        )
    
    elif callback.data == "switch":
        # Переключаем режим
        import config
        import importlib
        importlib.reload(config)
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
            await callback.message.edit_text(
                '⚡️ Переключено на <b>РЕАЛЬНУЮ ТОРГОВЛЮ</b>! Будьте осторожны!',
                reply_markup=get_main_keyboard()
            )
        else:
            await callback.message.edit_text(
                '🟢 Переключено на <b>ДЕМО-РЕЖИМ</b>.',
                reply_markup=get_main_keyboard()
            )
    
    elif callback.data == "settings":
        import config
        settings_info = f"""
<b>⚙️ Настройки бота</b>

<b>Режим торговли:</b> {'🟢 ВКЛЮЧЕНА' if config.ENABLE_TRADING else '🔴 ОТКЛЮЧЕНА'}
<b>Демо-режим:</b> {'🟢 ВКЛЮЧЕН' if config.DEMO_MODE else '🔴 ОТКЛЮЧЕН'}

<b>Параметры стратегии:</b>
• Тело свечи: {config.CANDLE_BODY_THRESHOLD}%
• Период объема: {config.VOLUME_PERIOD}
• Тейк-профит: {config.TAKE_PROFIT_PERCENT}%
• Стоп-лосс: {config.STOP_LOSS_PERCENT}%
• Размер позиции: {config.POSITION_SIZE_PERCENT}%
• Плечо: x{config.LEVERAGE}

<b>Баланс:</b> ${trader.get_balance():.2f}
<b>Цель:</b> ${config.TARGET_BALANCE}
"""
        await callback.message.edit_text(
            settings_info,
            reply_markup=get_main_keyboard()
        )

# --- Запуск ---
async def main():
    logger.info("Запуск Telegram-бота...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 