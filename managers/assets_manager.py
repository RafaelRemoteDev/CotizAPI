import yfinance as yf
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from db.database import SessionLocal, Asset
from typing import Generator, Optional, List
from sqlalchemy import text


def get_db() -> Generator[Session, None, None]:
    """
    Provides a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_price(symbol: str) -> float:
    """
    Retrieve the latest price of an asset.
    """
    try:
        with SessionLocal() as db:
            query = text("SELECT price FROM assets WHERE symbol = :symbol ORDER BY date DESC LIMIT 1")
            result = db.execute(query, {"symbol": symbol}).fetchone()

            if result is None or result[0] is None:
                print(f"⚠ Warning: No price data found for {symbol}")
                return None

            return float(result[0])
    except Exception as e:
        print(f"⚠ Error retrieving price for {symbol}: {e}")
        return None


def insert_price(db: Session, symbol: str, price: float, date: str) -> None:
    """
    Inserts or updates the price of an asset in the database.
    """
    try:
        # Try to update if the price already exists
        query_update = text("""
            UPDATE assets 
            SET price = :price 
            WHERE symbol = :symbol AND date = :date
        """)
        result = db.execute(query_update, {"symbol": symbol.upper(), "date": date, "price": price})
        db.commit()

        # If no rows were updated, insert a new record
        if result.rowcount == 0:
            query_insert = text("""
                INSERT INTO assets (symbol, date, price) 
                VALUES (:symbol, :date, :price)
            """)
            db.execute(query_insert, {"symbol": symbol.upper(), "date": date, "price": price})
            db.commit()

    except Exception as e:
        print(f"⚠ Error inserting/updating price for {symbol} on {date}: {e}")
        db.rollback()


def get_price_by_date(db: Session, symbol: str, date: str) -> Optional[float]:
    """
    Retrieves the price of an asset for a specific date.
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
        print(f"⚠ Error retrieving price for {symbol} on {date}: {e}")
        return None


def calculate_variations(assets: List[str], days: int) -> List[dict]:
    """
    Calculate percentage variations for asset prices.
    """
    variations = []
    db = SessionLocal()
    try:
        for symbol in assets:
            current_price = get_current_price(symbol)
            past_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            past_price = get_price_by_date(db, symbol, past_date)

            print(f"🔎 {symbol} - Current price: {current_price}, Price {days} days ago ({past_date}): {past_price}")

            if current_price is not None and past_price is not None:
                variation = ((current_price - past_price) / past_price) * 100
                variations.append({"symbol": symbol, "variation": variation})
            else:
                variations.append({"symbol": symbol, "variation": None})
    finally:
        db.close()

    return variations


def update_all_prices() -> None:
    """
    Updates asset prices and stores them in the database.
    """
    assets = ["GC=F", "SI=F", "BTC-USD", "ZW=F", "CL=F"]
    db: Session = SessionLocal()

    try:
        updated_prices = [(symbol, price) for symbol in assets if (price := get_current_price(symbol)) is not None]

        for symbol, price in updated_prices:
            date = datetime.now().strftime('%Y-%m-%d')
            insert_price(db, symbol, price, date)
            print(f"🔄 Updated: {symbol} - {price:.2f} USD")

    except Exception as e:
        print(f"⚠ Error updating prices: {e}")
    finally:
        db.close()










