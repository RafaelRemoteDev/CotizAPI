import telebot
import time
import requests
from loguru import logger
from datetime import datetime
from config import TELEGRAM_BOT_TOKEN, ASSETS_DICT

# Create bot instance
bot = None
if TELEGRAM_BOT_TOKEN:
    bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
    logger.info("Telegram bot initialized successfully")
else:
    logger.warning("TELEGRAM_BOT_TOKEN not configured. Bot will not be available.")


def aggressive_webhook_removal():
    """
    Aggressively remove webhook using multiple methods
    """
    if not TELEGRAM_BOT_TOKEN:
        return False

    methods_tried = []

    # Method 1: Direct API call
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteWebhook"
        params = {'drop_pending_updates': True}
        response = requests.post(url, json=params, timeout=15)
        result = response.json()

        methods_tried.append(f"API call: {result.get('ok', False)}")

        if result.get('ok'):
            logger.info("Webhook removed via API")
            time.sleep(2)
    except Exception as e:
        methods_tried.append(f"API call failed: {e}")

    # Method 2: Bot method
    try:
        if bot:
            bot.remove_webhook(drop_pending_updates=True)
            methods_tried.append("Bot method: executed")
            logger.info("Webhook removal via bot method")
            time.sleep(2)
    except Exception as e:
        methods_tried.append(f"Bot method failed: {e}")

    # Method 3: Verify removal
    try:
        check_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getWebhookInfo"
        check_response = requests.get(check_url, timeout=15)
        check_result = check_response.json()

        if check_result.get('ok'):
            webhook_info = check_result['result']
            has_webhook = bool(webhook_info.get('url'))
            methods_tried.append(f"Verification: webhook_active={has_webhook}")

            if not has_webhook:
                logger.info("Webhook successfully removed - verified")
                return True
            else:
                logger.warning(f"Webhook still active: {webhook_info.get('url')}")
                return False
        else:
            methods_tried.append("Verification failed")
            return False

    except Exception as e:
        methods_tried.append(f"Verification error: {e}")
        return False


def setup_bot_handlers():
    """
    Setup all bot command handlers
    """
    if not bot:
        return

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        welcome_text = """
Welcome to CotizAPI Bot!

Available commands:
/start - Show this welcome message
/assets - List monitored assets
/daily - Daily price variations
/weekly - Weekly price variations
/monthly - Monthly price variations
/alerts - Recent price alerts
/update - Force price update

This bot uses polling mode (no webhooks).
        """
        bot.reply_to(message, welcome_text)
        logger.info(f"User {message.from_user.username or message.from_user.id} started bot")

    @bot.message_handler(commands=['assets'])
    def send_assets(message):
        try:
            logger.info(f"User {message.from_user.username or message.from_user.id} requested assets with prices")

            loading_msg = bot.reply_to(message, "Fetching current asset prices...")

            try:
                from managers.assets_manager import get_current_price_db

                assets_text = "Currently Monitored Assets:\n\n"

                for symbol, name in ASSETS_DICT.items():
                    # Get current price from database
                    price = get_current_price_db(symbol)

                    if price and price > 0:
                        assets_text += f"{name} ({symbol}): ${price:.2f}\n"
                    else:
                        assets_text += f"{name} ({symbol}): Price unavailable\n"

                assets_text += "\nUse /daily, /weekly, or /monthly for variations"
                assets_text += "\nData source: Yahoo Finance"
                assets_text += f"\nLast updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                assets_text += "\nPowered by CotizAPI"

                bot.edit_message_text(
                    assets_text,
                    chat_id=loading_msg.chat.id,
                    message_id=loading_msg.message_id
                )

            except Exception as e:
                logger.error(f"Error fetching asset prices: {e}")
                bot.edit_message_text(
                    "Error retrieving asset prices",
                    chat_id=loading_msg.chat.id,
                    message_id=loading_msg.message_id
                )

        except Exception as e:
            logger.error(f"Error in assets command: {e}")
            bot.reply_to(message, "Error retrieving assets information.")

    @bot.message_handler(commands=['daily'])
    def send_daily_variations(message):
        try:
            logger.info(f"User {message.from_user.username or message.from_user.id} requested daily variations")

            loading_msg = bot.reply_to(message, "Calculating daily variations...")

            try:
                from managers.assets_manager import calculate_variations

                daily_variations = calculate_variations(list(ASSETS_DICT.keys()), 1)

                if daily_variations:
                    response = "Daily Price Variations (24h):\n\n"

                    for item in daily_variations:
                        symbol = item["symbol"]
                        variation = item["variation"]
                        name = ASSETS_DICT.get(symbol, symbol)

                        if variation is not None:
                            response += f"{name}: {variation:+.2f}%\n"
                        else:
                            response += f"{name}: No data available\n"

                    response += f"\nCalculated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    response += "\nPowered by CotizAPI"

                    bot.edit_message_text(
                        response,
                        chat_id=loading_msg.chat.id,
                        message_id=loading_msg.message_id
                    )
                else:
                    bot.edit_message_text(
                        "No variation data available",
                        chat_id=loading_msg.chat.id,
                        message_id=loading_msg.message_id
                    )

            except Exception as e:
                logger.error(f"Error calculating daily variations: {e}")
                bot.edit_message_text(
                    "Error calculating daily variations",
                    chat_id=loading_msg.chat.id,
                    message_id=loading_msg.message_id
                )

        except Exception as e:
            logger.error(f"Error in daily command: {e}")
            bot.reply_to(message, "Error processing daily variations command.")

    @bot.message_handler(commands=['weekly'])
    def send_weekly_variations(message):
        try:
            logger.info(f"User {message.from_user.username or message.from_user.id} requested weekly variations")

            loading_msg = bot.reply_to(message, "Calculating weekly variations...")

            try:
                from managers.assets_manager import calculate_variations

                weekly_variations = calculate_variations(list(ASSETS_DICT.keys()), 7)

                if weekly_variations:
                    response = "Weekly Price Variations (7 days):\n\n"

                    for item in weekly_variations:
                        symbol = item["symbol"]
                        variation = item["variation"]
                        name = ASSETS_DICT.get(symbol, symbol)

                        if variation is not None:
                            response += f"{name}: {variation:+.2f}%\n"
                        else:
                            response += f"{name}: No data available\n"

                    response += f"\nCalculated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    response += "\nPowered by CotizAPI"

                    bot.edit_message_text(
                        response,
                        chat_id=loading_msg.chat.id,
                        message_id=loading_msg.message_id
                    )
                else:
                    bot.edit_message_text(
                        "No variation data available",
                        chat_id=loading_msg.chat.id,
                        message_id=loading_msg.message_id
                    )

            except Exception as e:
                logger.error(f"Error calculating weekly variations: {e}")
                bot.edit_message_text(
                    "Error calculating weekly variations",
                    chat_id=loading_msg.chat.id,
                    message_id=loading_msg.message_id
                )

        except Exception as e:
            logger.error(f"Error in weekly command: {e}")
            bot.reply_to(message, "Error processing weekly variations command.")

    @bot.message_handler(commands=['monthly'])
    def send_monthly_variations(message):
        try:
            logger.info(f"User {message.from_user.username or message.from_user.id} requested monthly variations")

            loading_msg = bot.reply_to(message, "Calculating monthly variations...")

            try:
                from managers.assets_manager import calculate_variations

                monthly_variations = calculate_variations(list(ASSETS_DICT.keys()), 30)

                if monthly_variations:
                    response = "Monthly Price Variations (30 days):\n\n"

                    for item in monthly_variations:
                        symbol = item["symbol"]
                        variation = item["variation"]
                        name = ASSETS_DICT.get(symbol, symbol)

                        if variation is not None:
                            response += f"{name}: {variation:+.2f}%\n"
                        else:
                            response += f"{name}: No data available\n"

                    response += f"\nCalculated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    response += "\nPowered by CotizAPI"

                    bot.edit_message_text(
                        response,
                        chat_id=loading_msg.chat.id,
                        message_id=loading_msg.message_id
                    )
                else:
                    bot.edit_message_text(
                        "No variation data available",
                        chat_id=loading_msg.chat.id,
                        message_id=loading_msg.message_id
                    )

            except Exception as e:
                logger.error(f"Error calculating monthly variations: {e}")
                bot.edit_message_text(
                    "Error calculating monthly variations",
                    chat_id=loading_msg.chat.id,
                    message_id=loading_msg.message_id
                )

        except Exception as e:
            logger.error(f"Error in monthly command: {e}")
            bot.reply_to(message, "Error processing monthly variations command.")

    @bot.message_handler(commands=['alerts'])
    def send_alerts(message):
        try:
            logger.info(f"User {message.from_user.username or message.from_user.id} requested alerts")

            loading_msg = bot.reply_to(message, "Fetching recent alerts...")

            try:
                from managers.alerts_manager import get_recent_alerts

                alerts = get_recent_alerts()

                if alerts:
                    response = "Recent Price Alerts (24h):\n\n"

                    for alert in alerts:
                        symbol = alert["symbol"]
                        name = ASSETS_DICT.get(symbol, symbol)
                        message_text = alert["message"]
                        date = alert["date"]

                        response += f"{name}:\n"
                        response += f"   {message_text}\n"
                        response += f"   {date}\n\n"

                    response += "Powered by CotizAPI"

                    bot.edit_message_text(
                        response,
                        chat_id=loading_msg.chat.id,
                        message_id=loading_msg.message_id
                    )
                else:
                    bot.edit_message_text(
                        "No alerts in the last 24 hours.\nAll assets are within normal ranges.",
                        chat_id=loading_msg.chat.id,
                        message_id=loading_msg.message_id
                    )

            except Exception as e:
                logger.error(f"Error fetching alerts: {e}")
                bot.edit_message_text(
                    "Error fetching alerts",
                    chat_id=loading_msg.chat.id,
                    message_id=loading_msg.message_id
                )

        except Exception as e:
            logger.error(f"Error in alerts command: {e}")
            bot.reply_to(message, "Error processing alerts command.")

    @bot.message_handler(commands=['update'])
    def force_update(message):
        try:
            logger.info(f"User {message.from_user.username or message.from_user.id} requested force update")

            loading_msg = bot.reply_to(message, "Forcing price update from Yahoo Finance...")

            try:
                from managers.assets_manager import update_prices_efficiently

                result = update_prices_efficiently(force_update=True)

                if result.get('status') == 'success':
                    updated = result.get('updated_successfully', 0)
                    total = result.get('total_assets', 0)
                    failed = result.get('failed_assets', 0)

                    response = f"Price Update Complete!\n\n"
                    response += f"Successfully updated: {updated}/{total} assets\n"

                    if failed > 0:
                        response += f"Failed updates: {failed}\n"
                        failed_symbols = result.get('failed_symbols', [])
                        if failed_symbols:
                            response += f"Failed assets: {', '.join(failed_symbols)}\n"

                    response += f"\nUpdated: {result.get('date', 'Unknown')}"
                    response += "\nPowered by CotizAPI"

                    bot.edit_message_text(
                        response,
                        chat_id=loading_msg.chat.id,
                        message_id=loading_msg.message_id
                    )
                else:
                    bot.edit_message_text(
                        f"Update failed: {result.get('message', 'Unknown error')}",
                        chat_id=loading_msg.chat.id,
                        message_id=loading_msg.message_id
                    )

            except Exception as e:
                logger.error(f"Error in force update: {e}")
                bot.edit_message_text(
                    "Error during price update",
                    chat_id=loading_msg.chat.id,
                    message_id=loading_msg.message_id
                )

        except Exception as e:
            logger.error(f"Error in update command: {e}")
            bot.reply_to(message, "Error processing update command.")

    @bot.message_handler(func=lambda message: True)
    def handle_unknown(message):
        """Handle unknown commands and messages"""
        unknown_response = """
I don't understand that command.

CotizAPI Bot Commands:
/start - Welcome message
/assets - List assets
/daily - Daily variations
/weekly - Weekly variations  
/monthly - Monthly variations
/alerts - Recent alerts
/update - Force update

Type /start for more information.
        """
        bot.reply_to(message, unknown_response)

    logger.info("All bot message handlers configured successfully")


def start_bot():
    """
    Start the Telegram bot with webhook prevention
    """
    if not bot:
        logger.error("Cannot start bot - TELEGRAM_BOT_TOKEN not configured")
        return

    max_startup_attempts = 3

    for attempt in range(max_startup_attempts):
        try:
            logger.info(f"Bot startup attempt {attempt + 1}/{max_startup_attempts}")

            # Step 1: Aggressively remove any webhooks
            logger.info("Removing webhooks...")
            webhook_removed = False

            for webhook_attempt in range(3):
                if aggressive_webhook_removal():
                    webhook_removed = True
                    break
                else:
                    logger.warning(f"Webhook removal attempt {webhook_attempt + 1} failed")
                    if webhook_attempt < 2:
                        time.sleep(5)

            if not webhook_removed:
                logger.error("Failed to remove webhook after multiple attempts")
                if attempt < max_startup_attempts - 1:
                    logger.info("Retrying entire startup process...")
                    time.sleep(10)
                    continue
                else:
                    raise Exception("Webhook removal failed permanently")

            # Step 2: Test bot connectivity
            logger.info("Testing bot connection...")
            me = bot.get_me()
            logger.info(f"Bot connected successfully: @{me.username} ({me.first_name})")

            # Step 3: Setup command handlers
            setup_bot_handlers()

            # Step 4: Start polling with robust settings
            logger.info("Starting polling mode...")
            logger.info("Bot is now listening for messages...")

            bot.polling(
                non_stop=True,
                interval=1,
                timeout=60,
                skip_pending=True,
                allowed_updates=None
            )

            # If we reach here, polling ended unexpectedly
            logger.warning("Polling ended unexpectedly")
            break

        except telebot.apihelper.ApiTelegramException as e:
            if e.error_code == 409:
                logger.error(f"Webhook conflict on startup attempt {attempt + 1}")
                logger.error("Another webhook is still active!")

                if attempt < max_startup_attempts - 1:
                    wait_time = 15 + (attempt * 10)
                    logger.info(f"Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    logger.error("Webhook conflict persists after all attempts")
                    logger.error("Manual intervention required:")
                    logger.error("1. Run fix_webhook.py")
                    logger.error("2. Contact @BotFather to delete webhook")
                    logger.error("3. Check if another service is setting webhooks")
                    raise
            else:
                logger.error(f"Telegram API error: {e}")
                raise

        except Exception as e:
            logger.error(f"Bot startup error: {e}")
            if attempt < max_startup_attempts - 1:
                logger.info("Retrying startup in 10 seconds...")
                time.sleep(10)
            else:
                logger.error("Failed to start bot after all attempts")
                raise


# Test function
def test_bot_connectivity():
    """Test if bot can connect to Telegram"""
    if not bot:
        return False

    try:
        me = bot.get_me()
        logger.info(f"Bot connectivity test passed: @{me.username}")
        return True
    except Exception as e:
        logger.error(f"Bot connectivity test failed: {e}")
        return False


if __name__ == "__main__":
    # For direct testing
    start_bot()
