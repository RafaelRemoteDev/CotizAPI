import os
from datetime import datetime, timedelta
from typing import List, Optional

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

from managers.alerts_manager import get_recent_alerts, generate_alerts
from managers.assets_manager import get_current_price, get_db, get_price_by_date, insert_price
from sqlalchemy.orm import Session
from sqlalchemy import text
from db.database import SessionLocal

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("The Telegram BOT TOKEN is missing in the .env file")

# Asset dictionary
ASSETS = {
    "GC=F": "Gold 🥇",
    "SI=F": "Silver 🥈",
    "BTC-USD": "Bitcoin ₿",
    "ZW=F": "Wheat 🌾",
    "CL=F": "Oil 🛢️",
}


# Bot Commands
async def start(update: Update, context: CallbackContext):
    """
    Displays a welcome message and available commands.
    """
    await update.message.reply_text(
        "Hello, I'm CotizAPI! 🤖💸🐂\n"
        "Available commands:\n"
        "/assets - View current asset prices.\n"
        "/daily - Daily price variations.\n"
        "/weekly - Weekly price variations.\n"
        "/update - Update asset prices in the database.\n"
        "/alerts - View alerts generated in the last 24 hours.\n"
    )


async def assets(update: Update, context: CallbackContext):
    """
    Retrieves and displays the latest prices for all tracked assets.
    """
    messages = []
    for symbol, name in ASSETS.items():
        price = get_current_price(symbol)
        messages.append(f"{name}: {price:.2f} USD" if price else f"{name}: Price not available.")

    await update.message.reply_text("\n".join(messages))


async def update_prices(update: Update, context: CallbackContext):
    """
    Fetches new asset prices from Yahoo Finance, updates the database, and sends results to the user.
    """
    await update.message.reply_text("⏳ Fetching the latest asset prices...")

    from services.yahoo_finance import get_current_price  # Ensure fetching from API
    from managers.assets_manager import insert_price
    from sqlalchemy.orm import Session
    from db.database import SessionLocal

    assets = ["GC=F", "SI=F", "BTC-USD", "ZW=F", "CL=F"]
    db: Session = SessionLocal()

    messages = []
    try:
        for symbol in assets:
            price = get_current_price(symbol)  # Fetch the latest price from Yahoo Finance
            if price is not None:
                date = datetime.now().strftime('%Y-%m-%d')  # Get the current date (YYYY-MM-DD)
                insert_price(db, symbol, price, date)  # Store it in the database
                message = f"🔄 Updated: {symbol} - {price:.2f} USD"
                messages.append(message)
            else:
                messages.append(f"⚠ Warning: No price available for {symbol}")

        await update.message.reply_text("\n".join(messages))  # Send update to the user

    except Exception as e:
        await update.message.reply_text(f"⚠ Error updating prices: {e}")
    finally:
        db.close()


async def daily(update: Update, context: CallbackContext):
    """
    Displays daily price variations for assets.
    """
    messages = []
    db = SessionLocal()

    try:
        for symbol, name in ASSETS.items():
            current_price = get_current_price(symbol)  # Gets the latest price

            if current_price:
                reference_price = None
                reference_date = None

                # Try finding a price from yesterday, or from previous days if missing
                for days in range(1, 5):
                    date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
                    reference_price = get_price_by_date(db, symbol, date)
                    if reference_price:
                        reference_date = date
                        break

                if reference_price:
                    variation = ((current_price - reference_price) / reference_price) * 100
                    messages.append(f"{name}: Daily change {variation:.2f}% (Based on {reference_date})")
                else:
                    messages.append(f"{name}: Not enough data to calculate daily variation.")
            else:
                messages.append(f"{name}: Current price unavailable.")

        await update.message.reply_text("\n".join(messages))

    except Exception as e:
        print(f"Error processing daily variation: {e}")
    finally:
        db.close()


async def weekly(update: Update, context: CallbackContext):
    """
    Displays weekly price variations for assets.
    """
    messages = []
    db = SessionLocal()

    try:
        for symbol, name in ASSETS.items():
            current_price = get_current_price(symbol)
            if current_price:
                reference_price = None
                reference_date = None

                for days in [7, 8, 9]:
                    date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
                    reference_price = get_price_by_date(db, symbol, date)
                    if reference_price:
                        reference_date = date
                        break

                if reference_price:
                    variation = ((current_price - reference_price) / reference_price) * 100
                    messages.append(f"{name}: Weekly change {variation:.2f}% (Based on {reference_date})")
                else:
                    messages.append(f"{name}: Not enough data to calculate weekly variation.")
            else:
                messages.append(f"{name}: Current price unavailable.")

        await update.message.reply_text("\n".join(messages))

    except Exception as e:
        print(f"Error processing weekly variation: {e}")
    finally:
        db.close()


async def alerts(update: Update, context: CallbackContext):
    """
    Displays recent alerts from the last 24 hours.
    """
    alert_list = get_recent_alerts()
    if not alert_list:
        await update.message.reply_text("✅ No alerts recorded in the last 24 hours.")
        return

    messages = [
        f"🔔 Alert for {alert['symbol']}! {alert['message']} (Date: {alert['date']})"
        for alert in alert_list
    ]

    print(f"📢 Sending alerts -> {messages}")

    await update.message.reply_text("\n".join(messages), parse_mode="HTML")


def main():
    """
    Initializes the Telegram bot and registers commands.
    """
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("assets", assets))
    application.add_handler(CommandHandler("update", update_prices))
    application.add_handler(CommandHandler("daily", daily))
    application.add_handler(CommandHandler("weekly", weekly))
    application.add_handler(CommandHandler("alerts", alerts))

    print("🤖 Bot is running...")
    application.run_polling()
