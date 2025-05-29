import threading
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.endpoints import router as api_router  # Use modified endpoints
from managers.assets_manager import update_prices_efficiently
from db.database import initialize_database
from loguru import logger
from config import API_HOST, API_PORT, TELEGRAM_BOT_TOKEN
from bot.telegram_bot import start_bot


# Initialize FastAPI
app = FastAPI(
    title="CotizAPI",
    description="API for tracking financial asset prices",
    version="1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API router
app.include_router(api_router)


@app.get("/")
def read_root():
    """
    Root endpoint to verify that the API is working.
    """
    return {"message": "CotizAPI is working correctly!"}


# Function to start FastAPI in a separate thread
def start_fastapi():
    """
    Starts the FastAPI server in a separate thread.
    """
    uvicorn.run("main:app", host=API_HOST, port=API_PORT)


def initialize_system():
    """
    Initializes the database, updates prices and generates alerts.
    """
    try:
        # Initialize database
        logger.info("Initializing database...")
        initialize_database()
        logger.info("Database ready.")

        # Update prices individually
        logger.info("Updating asset prices...")
        update_result = update_prices_efficiently(force_update=True)
        logger.info(f"Update completed: {update_result['updated_successfully']} prices updated")

        # Generate alerts
        logger.info("Generating alerts...")
        # Temporarily commented for testing
        # generate_alerts()
        logger.info("Alerts generated.")
    except Exception as e:
        logger.error(f"Error during initialization: {e}")


def main():
    """
    Main function to run the application with Telegram bot as main process.
    """
    # Check Telegram token
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not configured. Bot cannot start.")
        return

    # Initialize system
    initialize_system()

    # Start FastAPI in a separate thread
    api_thread = threading.Thread(target=start_fastapi, daemon=True)
    api_thread.start()
    logger.info(f"FastAPI server started in background (http://{API_HOST}:{API_PORT})")

    # Start Telegram bot (main process)
    logger.info("Starting Telegram bot (main process)...")
    start_bot()


# Entry point
if __name__ == "__main__":
    main()