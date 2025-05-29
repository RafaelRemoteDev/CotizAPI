import telebot
from loguru import logger
from config import TELEGRAM_BOT_TOKEN
from .handlers import setup_bot_handlers

# Create Telegram bot
bot = None
if TELEGRAM_BOT_TOKEN:
    bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
    setup_bot_handlers(bot)
    logger.info("Telegram bot initialized successfully")
else:
    logger.warning("TELEGRAM_BOT_TOKEN not configured. Bot will not be available.")


def start_bot():
    """
    Starts the Telegram bot.
    """
    if bot:
        logger.info("Starting Telegram bot...")
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            logger.error(f"Error in Telegram bot: {e}")
    else:
        logger.warning("Cannot start bot because it is not properly configured.")
