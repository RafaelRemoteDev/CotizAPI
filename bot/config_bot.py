from telegram import Bot
from telegram.error import TelegramError
from loguru import logger
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


async def send_telegram_message(message: str) -> bool:
    """
    Sends a message to a Telegram chat.
    Requires both TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to be configured.

    Args:
    ----
        message: The message to send.

    Returns:
    -------
        True if message was sent successfully, False otherwise.
    """
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not configured")
        return False

    if not TELEGRAM_CHAT_ID:
        logger.warning("TELEGRAM_CHAT_ID is not configured. Cannot send automatic alerts.")
        logger.info("Users can get their Chat ID by sending /chatid to the bot.")
        return False

    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.info(f"Telegram message sent: {message[:50]}...")
        return True
    except TelegramError as e:
        logger.error(f"Error sending Telegram message: {e}")
        return False
