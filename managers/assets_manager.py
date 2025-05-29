from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from loguru import logger

from config import ASSETS
from db.database import SessionLocal


def get_current_price_db(symbol: str) -> float | None:
    """
    Retrieve the latest price of an asset from the database.

    Args:
    ----
        symbol: Asset symbol.

    Returns:
    -------
        Current price or None if not available.
    """
    try:
        with SessionLocal() as db:
            query = text("SELECT price FROM assets WHERE symbol = :symbol ORDER BY date DESC LIMIT 1")
            result = db.execute(query, {"symbol": symbol}).fetchone()

            if result is None or result[0] is None:
                logger.warning(f"No price data found for {symbol}")
                return None

            return float(result[0])
    except Exception as e:
        logger.error(f"Error retrieving price for {symbol}: {e}")
        return None


def get_price_by_date(db: Session, symbol: str, date: str) -> float | None:
    """
    Retrieves the price of an asset for a specific date from database.

    Args:
    ----
        db: Database session.
        symbol: Asset symbol.
        date: Date for which to retrieve the price.

    Returns:
    -------
        Price on the specified date or None if not available.
    """
    try:
        query = text("""
            SELECT price FROM assets 
            WHERE symbol = :symbol AND date <= :date
            ORDER BY date DESC 
            LIMIT 1
        """)
        result = db.execute(query, {"symbol": symbol, "date": date}).fetchone()

        return float(result[0]) if result and result[0] is not None else None
    except Exception as e:
        logger.error(f"Error retrieving price for {symbol} on {date}: {e}")
        return None


def insert_price(db: Session, symbol: str, price: float, date: str) -> bool:
    """
    Inserts or updates the price of an asset in the database.

    Args:
    ----
        db: Database session.
        symbol: Asset symbol.
        price: Price value to insert.
        date: Date for the price record.

    Returns:
    -------
        True if operation was successful, False otherwise.
    """
    try:
        # Try to update first
        query_update = text("""
            UPDATE assets 
            SET price = :price 
            WHERE symbol = :symbol AND date = :date
        """)
        result = db.execute(query_update, {"symbol": symbol.upper(), "date": date, "price": price})
        db.commit()

        # If no record was updated, it doesn't exist and needs to be inserted
        if result.rowcount == 0:
            logger.info(f"No existing price for {symbol} on {date}, inserting new record.")
            query_insert = text("""
                INSERT INTO assets (symbol, date, price) 
                VALUES (:symbol, :date, :price)
            """)
            db.execute(query_insert, {"symbol": symbol.upper(), "date": date, "price": price})
            db.commit()
            logger.info(f"Inserted new price for {symbol} on {date}: {price}")
        else:
            logger.info(f"Updated price for {symbol} on {date}: {price}")

        return True
    except Exception as e:
        logger.error(f"Error inserting/updating price for {symbol} on {date}: {e}")
        db.rollback()
        return False


def calculate_variations(assets: List[str], days: int) -> List[dict]:
    """
    Calculate percentage variations for asset prices.

    Args:
    ----
        assets: List of asset symbols.
        days: Number of days for the variation calculation.

    Returns:
    -------
        List of dictionaries containing symbol and variation.
    """
    variations = []
    db = SessionLocal()
    try:
        for symbol in assets:
            current_price = get_current_price_db(symbol)
            past_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            past_price = get_price_by_date(db, symbol, past_date)

            logger.debug(
                f"{symbol} - Current price: {current_price}, Price {days} days ago ({past_date}): {past_price}")

            if current_price is not None and past_price is not None:
                variation = ((current_price - past_price) / past_price) * 100
                variations.append({"symbol": symbol, "variation": variation})
            else:
                variations.append({"symbol": symbol, "variation": None})
    finally:
        db.close()

    return variations


def update_single_price(symbol: str, price: float, date: str) -> bool:
    """
    Updates a single asset price in the database.

    Args:
    ----
        symbol: Asset symbol.
        price: New price value.
        date: Date for the price.

    Returns:
    -------
        True if successful, False otherwise.
    """
    db = SessionLocal()
    try:
        return insert_price(db, symbol, price, date)
    finally:
        db.close()


def update_prices_efficiently(force_update: bool = False) -> Dict[str, Any]:
    """
    Updates asset prices in the database.

    Args:
    ----
        force_update: Whether to force update even if prices exist for today.

    Returns:
    -------
        Dictionary with results summary.
    """
    import time
    from services.yahoo_finance import get_current_price as yahoo_get_current_price

    today = datetime.now().strftime('%Y-%m-%d')

    # Determine which symbols need updating
    symbols_to_update = []
    db = SessionLocal()
    try:
        if force_update:
            # If forcing update, update all symbols
            symbols_to_update = ASSETS.copy()
            logger.info(f"Force update requested for all assets: {', '.join(symbols_to_update)}")
        else:
            # If not forcing, only update those without today's price
            for symbol in ASSETS:
                query = text("""
                    SELECT COUNT(*) FROM assets 
                    WHERE symbol = :symbol AND date = :date
                """)
                result = db.execute(query, {"symbol": symbol, "date": today}).scalar()

                if result == 0:
                    symbols_to_update.append(symbol)

            if not symbols_to_update:
                logger.info(f"All assets already have prices for today ({today}). No update needed.")
                return {"status": "no_update_needed", "message": "All assets already have prices for today"}
    finally:
        db.close()

    logger.info(f"Fetching prices for {len(symbols_to_update)} assets: {', '.join(symbols_to_update)}")

    # Get current prices one by one
    success_count = 0
    failed_symbols = []

    for symbol in symbols_to_update:
        # Add delay between queries to avoid rate limits
        if symbol != symbols_to_update[0]:  # Don't wait for the first symbol
            wait_time = 5  # Wait 5 seconds between requests
            logger.info(f"Waiting {wait_time} seconds before requesting the next symbol...")
            time.sleep(wait_time)

        logger.info(f"Fetching price for {symbol}...")
        price = yahoo_get_current_price(symbol)

        if price is not None:
            # Update price in database
            if update_single_price(symbol, price, today):
                success_count += 1
                logger.info(f"Successfully updated price for {symbol}: {price:.2f} USD")
            else:
                failed_symbols.append(symbol)
                logger.error(f"Failed to save price for {symbol} in database")
        else:
            failed_symbols.append(symbol)
            logger.warning(f"Could not get a valid price for {symbol}")

    # Generate results summary
    results = {
        "status": "success" if success_count > 0 else "error",
        "total_assets": len(symbols_to_update),
        "updated_successfully": success_count,
        "failed_assets": len(failed_symbols),
        "failed_symbols": failed_symbols,
        "date": today,
        "force_update": force_update
    }

    if success_count > 0:
        logger.info(f"Successfully updated {success_count} out of {len(symbols_to_update)} assets")
    else:
        logger.error("Failed to update any asset prices")

    return results


def update_all_prices() -> Dict[str, Any]:
    """
    Updates all asset prices and stores them in the database.

    Returns:
    -------
        Dictionary with results of the update operation.
    """
    return update_prices_efficiently(force_update=True)


def get_asset_prices_and_variations(force_update: bool = True) -> Dict[str, Any]:
    """
    Gets current prices and variations for all assets.

    Args:
    ----
        force_update: Whether to force price update.

    Returns:
    -------
        Dictionary with current prices and variations.
    """
    # Update prices if necessary
    if force_update:
        logger.info("Updating asset prices...")
        update_results = update_prices_efficiently(force_update=force_update)
        logger.info(f"Update completed: {update_results['updated_successfully']} prices updated")

    # Get current prices from database
    current_prices = {}
    for symbol in ASSETS:
        price = get_current_price_db(symbol)
        if price is not None:
            current_prices[symbol] = price

    # Calculate variations
    logger.info("Calculating variations...")
    daily_variations = calculate_variations(ASSETS, 1)
    weekly_variations = calculate_variations(ASSETS, 7)
    monthly_variations = calculate_variations(ASSETS, 30)

    # Organize results
    result = {
        "current_prices": current_prices,
        "daily_variations": {var["symbol"]: var["variation"] for var in daily_variations},
        "weekly_variations": {var["symbol"]: var["variation"] for var in weekly_variations},
        "monthly_variations": {var["symbol"]: var["variation"] for var in monthly_variations},
        "last_update": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    return result
