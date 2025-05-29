import yfinance as yf
from datetime import datetime
import time
import random
from loguru import logger


def is_weekend() -> bool:
    """
    Checks if today is a weekend (Saturday or Sunday).

    Returns:
    -------
        True if it's weekend, False otherwise.
    """
    weekday = datetime.now().weekday()
    return weekday >= 5  # 5 = Saturday, 6 = Sunday


def get_current_price(symbol: str) -> float | None:
    """
    Retrieves the latest available price of an asset from Yahoo Finance.
    Implements a simple retry mechanism with delay.

    Args:
    ----
        symbol: Asset symbol.

    Returns:
    -------
        Current price or None if not available.
    """
    max_retries = 3

    for attempt in range(max_retries):
        try:
            # If not the first attempt, wait with exponential backoff
            if attempt > 0:
                wait_time = (2 ** attempt) + random.uniform(1, 3)
                logger.debug(f"Retrying {symbol} in {wait_time:.2f} seconds (attempt {attempt + 1}/{max_retries})...")
                time.sleep(wait_time)

            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d")

            if not data.empty and 'Close' in data.columns:
                price = float(data['Close'].iloc[-1])
                logger.info(f"{symbol}: Last price from Yahoo: {price:.2f} USD")
                return price
            else:
                logger.warning(f"No data available for {symbol}")

        except Exception as e:
            logger.warning(f"Attempt {attempt + 1}/{max_retries} failed for {symbol}: {e}")
            if attempt == max_retries - 1:
                logger.error(f"All retries failed for {symbol}: {e}")

    return None


def get_multiple_prices(symbols: list[str]) -> dict[str, float | None]:
    """
    Gets current prices for multiple assets with a patient approach.
    Gets each symbol individually with delays to avoid rate limits.

    Args:
    ----
        symbols: List of asset symbols.

    Returns:
    -------
        Dictionary with symbols as keys and prices as values.
    """
    if is_weekend():
        logger.warning("Today is weekend. Market prices may not be up-to-date.")

    results = {}

    # Process symbols one by one with delays between requests
    for symbol in symbols:
        # Add random delay between requests
        if symbol != symbols[0]:  # Don't wait for the first symbol
            wait_time = random.uniform(3, 6)  # Wait between 3 and 6 seconds
            logger.debug(f"Waiting {wait_time:.2f} seconds before requesting {symbol}...")
            time.sleep(wait_time)

        # Get individual price with retries
        price = get_current_price(symbol)
        results[symbol] = price

        if price is not None:
            logger.info(f"Successfully got price for {symbol}: {price:.2f} USD")
        else:
            logger.warning(f"Could not get price for {symbol} after retries")

    return results


