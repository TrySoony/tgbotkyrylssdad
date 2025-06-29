import asyncio
from aiogram import Bot
from aiogram.enums import ParseMode
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_ADMIN_ID
import logging

logger = logging.getLogger("notifications")

# Создаём глобальную переменную для бота
bot = None

def init_bot():
    """Инициализация бота для уведомлений."""
    global bot
    if bot is None:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)

async def send_trade_notification(text: str):
    """Отправка уведомления о сделке админу."""
    try:
        if bot is None:
            init_bot()
        await bot.send_message(chat_id=TELEGRAM_ADMIN_ID, text=text, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления: {e}")

def send_trade_notification_sync(text: str):
    """Синхронная версия отправки уведомления."""
    try:
        asyncio.create_task(send_trade_notification(text))
    except Exception as e:
        logger.error(f"Ошибка создания задачи отправки уведомления: {e}") 