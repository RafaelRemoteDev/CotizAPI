import uvicorn
import threading
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI
from api.endpoints import router as api_router
from bot.config_bot import main as bot_main
from managers.assets_manager import update_all_prices
from db.database import initialize_database

# ✅ Load environment variables
load_dotenv()

# ✅ Initialize FastAPI App
app = FastAPI(
    title="CotizAPI",
    description="API for tracking asset prices",
    version="1.0"
)

# ✅ Register API Router
app.include_router(api_router)

@app.get("/")
def read_root():
    return {"message": "CotizAPI is running correctly! 🤖💸🐂"}

def start_telegram_bot():
    """
    Starts the Telegram bot in a separate event loop.
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        print("🤖 Starting Telegram Bot...")
        loop.run_until_complete(bot_main())  # ✅ Correctly run async bot
    except Exception as e:
        print(f"⚠ Error starting Telegram Bot: {e}")

if __name__ == "__main__":
    try:
        print("⏳ Initializing database without deleting existing data...")
        initialize_database()
        print("✅ Database is ready.")

        print("🔄 Updating asset prices...")
        update_all_prices()
        print("✅ Prices updated.")

        # ✅ Start Telegram bot in a separate thread with asyncio loop
        bot_thread = threading.Thread(target=start_telegram_bot, daemon=True)
        bot_thread.start()

        print("🚀 Starting FastAPI Server...")
        uvicorn.run("main:app", host="127.0.0.1", port=8032, reload=True)

    except Exception as e:
        print(f"⚠ Critical Error: {e}")






