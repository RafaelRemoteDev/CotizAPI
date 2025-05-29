import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration
DATABASE_URL = "sqlite:///./cotizapi.db"

# API configuration
API_HOST = "127.0.0.1"  # Cambiado de 0.0.0.0 a 127.0.0.1
API_PORT = 8080

# Assets to track
ASSETS = ["GC=F", "SI=F", "BTC-USD", "ZW=F", "CL=F"]

# Assets with display names
ASSETS_DICT = {
    "GC=F": "Gold",
    "SI=F": "Silver",
    "BTC-USD": "Bitcoin",
    "ZW=F": "Wheat",
    "CL=F": "Oil",
}

# Threshold constants
DAILY_THRESHOLD = 3.0    # 3% daily variation threshold for alerts
WEEKLY_THRESHOLD = 6.0   # 6% weekly variation threshold for alerts
WEEK_DAY_THRESHOLD = 5   # Saturday is day 5 (0-indexed, Monday=0)

# Telegram Bot configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


ASSETS_DICT = {
    "GC=F": "Gold",
    "SI=F": "Silver",
    "BTC-USD": "Bitcoin",
    "ZW=F": "Wheat",
    "CL=F": "Oil",
}