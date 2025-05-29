from fastapi import APIRouter, Query, HTTPException
from typing import Dict, Any
from datetime import datetime
from sqlalchemy import text

from config import ASSETS, ASSETS_DICT
from managers.assets_manager import (
    get_current_price_db,
    update_prices_efficiently,
    calculate_variations,
    get_asset_prices_and_variations,
    update_single_price
)
from services.yahoo_finance import get_current_price as yahoo_get_current_price
from db.database import SessionLocal

# Define the router with the specific name 'router'
router = APIRouter(
    prefix="/api",
    tags=["api"],
    responses={404: {"description": "Not found"}},
)


@router.get("/assets", response_model=Dict[str, Any])
async def get_assets(
        force_update: bool = Query(True, description="Force price update from Yahoo Finance"),
):
    """
    Gets all asset prices and their variations.
    Updates prices every time it's called if force_update=True (default).

    Args:
    ----
        force_update: Whether to force update prices from Yahoo Finance.

    Returns:
    -------
        Dictionary containing current prices and variations for all assets.
    """
    # This endpoint automatically updates prices from Yahoo Finance
    return get_asset_prices_and_variations(force_update=force_update)


@router.get("/prices", response_model=Dict[str, Dict[str, Any]])
async def get_current_prices(
        force_update: bool = Query(True, description="Force price update from Yahoo Finance"),
):
    """
    Gets current asset prices, querying them directly from Yahoo Finance
    if force_update is True.

    Args:
    ----
        force_update: Whether to force update prices from Yahoo Finance.

    Returns:
    -------
        Dictionary containing current prices for all assets with metadata.
    """
    result = {}

    for symbol in ASSETS:
        name = ASSETS_DICT.get(symbol, symbol)
        asset_data = {"name": name}

        # If we should update, get direct price from Yahoo
        if force_update:
            price = yahoo_get_current_price(symbol)
            if price is not None:
                # Save to database
                today = datetime.now().strftime('%Y-%m-%d')
                update_single_price(symbol, price, today)
                asset_data["price"] = price
                asset_data["source"] = "yahoo_finance"
                asset_data["updated"] = True
            else:
                # Try to get from database as fallback
                db_price = get_current_price_db(symbol)
                asset_data["price"] = db_price
                asset_data["source"] = "database"
                asset_data["updated"] = False
        else:
            # Get directly from database
            db_price = get_current_price_db(symbol)
            asset_data["price"] = db_price
            asset_data["source"] = "database"
            asset_data["updated"] = False

        result[symbol] = asset_data

    return result


@router.get("/variations/{days}", response_model=Dict[str, Dict[str, Any]])
async def get_variations(
        days: int,
        force_update: bool = Query(False, description="Force price update before calculating variations"),
):
    """
    Gets price variations for a specific number of days.

    Args:
    ----
        days: Number of days for variation calculation (1=daily, 7=weekly, 30=monthly).
        force_update: Whether to force update current prices before calculation.

    Returns:
    -------
        Dictionary containing price variations for the specified period.
    """
    # Validate number of days
    if days <= 0:
        raise HTTPException(status_code=400, detail="Number of days must be greater than zero")

    # Update current prices if necessary
    if force_update:
        update_prices_efficiently(force_update=True)

    # Calculate variations
    variations_data = calculate_variations(ASSETS, days)

    # Convert to dictionary with descriptive names
    variations = {}
    for var in variations_data:
        symbol = var["symbol"]
        name = ASSETS_DICT.get(symbol, symbol)

        variations[symbol] = {
            "name": name,
            "variation": var["variation"],
            "days": days
        }

    return variations


@router.post("/update", response_model=Dict[str, Any])
async def force_update_prices():
    """
    Forces update of all asset prices directly from Yahoo Finance.

    Returns:
    -------
        Dictionary containing update operation results.
    """
    result = update_prices_efficiently(force_update=True)
    return result


@router.get("/latest/{symbol}", response_model=Dict[str, Any])
async def get_latest_price(
        symbol: str,
        force_update: bool = Query(True, description="Get price directly from Yahoo Finance"),
):
    """
    Gets the most recent price for a specific symbol.

    Args:
    ----
        symbol: Asset symbol (e.g. 'BTC-USD').
        force_update: Whether to get price directly from Yahoo Finance.

    Returns:
    -------
        Dictionary containing the latest price and metadata for the specified symbol.
    """
    # Validate symbol
    if symbol not in ASSETS:
        raise HTTPException(
            status_code=404,
            detail=f"Symbol '{symbol}' not found. Available symbols: {', '.join(ASSETS)}"
        )

    name = ASSETS_DICT.get(symbol, symbol)
    result = {"symbol": symbol, "name": name}

    # Get updated price if necessary
    if force_update:
        price = yahoo_get_current_price(symbol)
        if price is not None:
            # Save to database
            today = datetime.now().strftime('%Y-%m-%d')
            update_single_price(symbol, price, today)
            result["price"] = price
            result["source"] = "yahoo_finance"
            result["timestamp"] = datetime.now().isoformat()
            return result

    # If we didn't update or update failed, get from database
    db_price = get_current_price_db(symbol)
    if db_price is None:
        raise HTTPException(
            status_code=404,
            detail=f"No price found for {symbol} in database"
        )

    result["price"] = db_price
    result["source"] = "database"

    # Get price date
    db = SessionLocal()
    try:
        query = text("""
            SELECT date FROM assets 
            WHERE symbol = :symbol 
            ORDER BY date DESC 
            LIMIT 1
        """)
        date_result = db.execute(query, {"symbol": symbol}).fetchone()
        if date_result:
            result["date"] = date_result[0]
    finally:
        db.close()

    return result

