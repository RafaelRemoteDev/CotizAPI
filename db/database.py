from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator
from loguru import logger
from config import DATABASE_URL

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Models definition
class Asset(Base):
    """
    Model for storing asset prices.

    Attributes:
    ----------
        id: Primary key for the asset record.
        symbol: Financial instrument symbol (e.g., 'BTC-USD').
        price: Asset price value.
        date: Date when the price was recorded.
    """
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    price = Column(Float)
    date = Column(String)


class Alert(Base):
    """
    Model for storing price alerts.

    Attributes:
    ----------
        id: Primary key for the alert record.
        symbol: Financial instrument symbol that triggered the alert.
        date: Timestamp when the alert was generated.
        message: Alert message content.
    """
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    date = Column(DateTime)
    message = Column(String)


def get_db() -> Generator:
    """
    Dependency for FastAPI to get a database session.

    Yields:
    ------
        Database session that will be automatically closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def initialize_database():
    """
    Initializes the database, creating tables if they don't exist.

    Returns:
    -------
        None
    """
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")