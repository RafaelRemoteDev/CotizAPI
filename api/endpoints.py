from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel  # ✅ Using Pydantic for response validation
from managers.alerts_manager import get_recent_alerts
from managers.assets_manager import get_current_price, calculate_variations

router = APIRouter()

# ✅ Define tracked assets
ASSETS = ["GC=F", "SI=F", "BTC-USD", "ZW=F", "CL=F"]

# ✅ Pydantic Models for API responses
class AssetResponse(BaseModel):
    symbol: str  # ✅ Changed from "simbolo" to "symbol"
    price: Optional[float]  # ✅ Changed from "precio" to "price"

class VariationResponse(BaseModel):
    symbol: str  # ✅ Changed from "simbolo" to "symbol"
    variation: Optional[float]  # ✅ Changed from "variacion" to "variation"

class AlertResponse(BaseModel):
    symbol: str  # ✅ Changed from "simbolo" to "symbol"
    date: str  # ✅ Changed from "fecha" to "date"
    message: str  # ✅ Changed from "mensaje" to "message"

@router.get("/", summary="Welcome Message")
def endpoint_start():
    """
    Endpoint to display available API commands.
    """
    return {
        "message": "Welcome to CotizAPI! 🤖💸🐂",
        "endpoints": {
            "/assets": "Get current asset prices.",
            "/daily": "View daily price variations.",
            "/weekly": "View weekly price variations.",
            "/alerts": "View recent alerts generated.",
        }
    }

@router.get("/assets", response_model=List[AssetResponse])
def endpoint_assets():
    """
    Endpoint to get current asset prices.
    """
    try:
        return [{"symbol": symbol, "price": get_current_price(symbol)} for symbol in ASSETS]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving asset prices: {str(e)}")


@router.get("/daily", response_model=List[VariationResponse])
def endpoint_daily():
    """
    Endpoint to get daily price variations for assets.
    """
    try:
        variations = calculate_variations(ASSETS, 1)
        print(f"✅ Daily variations calculated: {variations}")

        return [{"symbol": item.get("symbol", "Unknown"), "variation": item.get("variation")} for item in variations]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating daily variations: {str(e)}")


@router.get("/weekly", response_model=List[VariationResponse])
def endpoint_weekly():
    """
    Endpoint to get weekly price variations for assets.
    """
    try:
        variations = calculate_variations(ASSETS, 7)
        return [{"symbol": item.get("symbol", "Unknown"), "variation": item.get("variation")} for item in variations]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating weekly variations: {str(e)}")

@router.get("/alerts", response_model=List[AlertResponse])
def endpoint_alerts():
    """
    Endpoint to get recent alerts (last 24 hours).
    """
    try:
        alerts = get_recent_alerts()
        if not alerts:
            raise HTTPException(status_code=404, detail="No alerts recorded in the last 24 hours.")
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving alerts: {str(e)}")











