from sqlalchemy import create_engine, Column, Integer, String, Float, Date, text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
import datetime

# Database URL (SQLite)
DATABASE_URL = "sqlite:///cotizapi.db"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ORM Base
class Base(DeclarativeBase):  # Updated to SQLAlchemy 2.0 standard
    pass


# **Assets Table**
class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    price = Column(Float, nullable=False)

    __table_args__ = (UniqueConstraint('symbol', 'date', name='uix_symbol_date'),)  # ✅ Unique constraint


# **Alerts Table**
class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, nullable=False)
    date = Column(Date, default=datetime.date.today)  # ✅ Now using DATE, not DATETIME
    message = Column(String, nullable=False)


# **Initialize database**
def initialize_database():
    """Creates tables if they do not exist."""
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully.")


# **Fetch the latest price of an asset by symbol**
def get_asset_price(symbol: str) -> float:
    """Returns the latest price of the given asset symbol."""
    session = SessionLocal()
    try:
        query = text("SELECT price FROM assets WHERE symbol = :symbol ORDER BY date DESC LIMIT 1")
        result = session.execute(query, {"symbol": symbol}).fetchone()

        return float(result[0]) if result and result[0] is not None else None  # ✅ Ensure proper handling of None values
    except Exception as e:
        print(f"⚠ Error retrieving price for {symbol}: {e}")
        return None
    finally:
        session.close()


# **Example of database initialization and testing**
if __name__ == "__main__":
    initialize_database()









