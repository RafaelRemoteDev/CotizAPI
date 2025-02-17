import yfinance as yf
from datetime import datetime
from typing import Optional, Dict, List
import time


def is_weekend() -> bool:
    """ Checks if today is a weekend (Saturday or Sunday). """
    return datetime.now().weekday() >= 5  # Saturday (5) or Sunday (6)


def get_current_price(symbol: str) -> Optional[float]:
    """
    Retrieves the latest available price of an asset from Yahoo Finance.

    :param symbol: The asset's ticker symbol.
    :return: The latest price as a float, or None if an error occurs.
    """
    try:
        ticker = yf.Ticker(symbol)

        # Treat Bitcoin separately as it operates 24/7
        if "BTC" in symbol:
            history = ticker.history(period="1d", interval="5m")
        else:
            history = ticker.history(period="1d", interval="1h")  # Use 1-hour interval for better availability

        if history.empty:
            print(f"⚠ No recent data available for {symbol}. Trying last 7 days...")
            history = ticker.history(period="7d", interval="1d").dropna()

            if history.empty:
                print(f"⚠ No historical data available for {symbol}. Skipping.")
                return None

        # Extract the last available date
        last_date = history.index[-1]
        price = history["Close"].iloc[-1]

        print(f"✅ {symbol}: Last available price: {price:.2f} USD (Date: {last_date})")
        return price

    except Exception as e:
        print(f"⚠ Error retrieving price for {symbol}: {e}")
        return None


def update_prices(assets: List[str]) -> Dict[str, Optional[float]]:
    """
    Updates the prices for a list of assets.

    :param assets: List of asset ticker symbols.
    :return: Dictionary with the updated prices.
    """
    if is_weekend():
        print("⚠ The market is closed. Prices will not be updated today.")
        return {}

    results: Dict[str, Optional[float]] = {}

    for symbol in assets:
        print(f"🔄 Updating price for {symbol}...")
        time.sleep(2)  # Prevent request blocking by Yahoo Finance
        price = get_current_price(symbol)

        if price is not None:
            results[symbol] = price
            print(f"✅ {symbol}: Last updated price: {price:.2f} USD")
        else:
            print(f"⚠ Could not update the price for {symbol}.")
            results[symbol] = None

    return results


# Execution of the script
if __name__ == "__main__":
    assets_list = ["GC=F", "SI=F", "BTC-USD", "ZW=F", "CL=F"]
    updated_prices = update_prices(assets_list)

    print("\n📊 Final Results:")
    for symbol, price in updated_prices.items():
        print(f"🔹 {symbol}: {price if price else 'Price unavailable'}")


