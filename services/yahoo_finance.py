import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional, Dict, List


def is_weekend() -> bool:
    """
    Checks if the current day is a weekend (Saturday or Sunday).

    :return: True if it's a weekend, False otherwise.
    """
    today: int = datetime.now().weekday()  # Monday=0, Sunday=6
    return today >= 5  # Saturday (5) or Sunday (6)


def get_current_price(symbol: str) -> Optional[float]:
    """
    Retrieves the current price of an asset from Yahoo Finance.

    :param symbol: The asset's ticker symbol.
    :return: The current price as a float, or None if an error occurs.
    """
    try:
        ticker = yf.Ticker(symbol)
        history = ticker.history(period="1d")

        # If no data is available for today, try the last available price
        if history.empty:
            print(f"⚠ No data for {symbol} today. Trying last available price...")
            history = ticker.history(period="7d").dropna()

            if history.empty:
                print(f"⚠ No historical data available for {symbol}. Skipping.")
                return None

        price: float = history["Close"].iloc[-1]
        print(f"✅ Retrieved price for {symbol}: {price:.2f} USD")
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
    results: Dict[str, Optional[float]] = {}

    for symbol in assets:
        print(f"🔄 Updating price for {symbol}...")
        price: Optional[float] = get_current_price(symbol)

        if price is not None:
            results[symbol] = price
            print(f"✅ {symbol}: Last updated price: {price:.2f} USD")
        else:
            print(f"⚠ Could not update the price for {symbol}.")
            results[symbol] = None

    return results


# Example usage:
if __name__ == "__main__":
    assets_list: List[str] = ["GC=F", "SI=F", "BTC-USD", "ZW=F", "CL=F"]
    updated_prices = update_prices(assets_list)

    print("\n📊 Final Results:")
    for symbol, price in updated_prices.items():
        print(f"🔹 {symbol}: {price if price else 'Price unavailable'}")

