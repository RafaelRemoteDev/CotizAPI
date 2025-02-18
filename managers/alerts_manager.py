from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from db.database import SessionLocal, Alert  # ✅ Renamed from Alerta
from managers.assets_manager import calculate_variations

# Thresholds for alerts
DAILY_THRESHOLD: float = 3.0  # 3% daily variation
WEEKLY_THRESHOLD: float = 6.0  # 6% weekly variation
ASSETS: list[str] = ["GC=F", "SI=F", "BTC-USD", "ZW=F", "CL=F"]


def generate_alerts() -> None:
    """
    Generates alerts based on price variations exceeding predefined thresholds.
    Alerts are created when:
    - The daily variation exceeds 3%.
    - The weekly variation exceeds 6%.
    """
    db: Session = SessionLocal()
    try:
        daily_variations: list[dict] = calculate_variations(ASSETS, 1)
        weekly_variations: list[dict] = calculate_variations(ASSETS, 7)

        for asset in ASSETS:
            # Check daily variation
            daily_variation: float = next(
                (item["variation"] for item in daily_variations if item["symbol"] == asset), None
            )
            if daily_variation is not None and abs(daily_variation) > DAILY_THRESHOLD:
                message: str = f"Daily variation of {daily_variation:.2f}% exceeded the threshold!"
                insert_alert(db, asset, message)

            # Check weekly variation
            weekly_variation: float = next(
                (item["variation"] for item in weekly_variations if item["symbol"] == asset), None
            )
            if weekly_variation is not None and abs(weekly_variation) > WEEKLY_THRESHOLD:
                message: str = f"Weekly variation of {weekly_variation:.2f}% exceeded the threshold!"
                insert_alert(db, asset, message)

        print("✅ Alerts generated successfully.")
    finally:
        db.close()


def insert_alert(db: Session, symbol: str, message: str) -> None:
    """
    Inserts a new alert into the database.
    """
    print(f"🚨 Inserting alert -> Symbol: {symbol} | Message: {message}")
    new_alert = Alert(symbol=symbol, date=datetime.utcnow(), message=message)
    db.add(new_alert)
    db.commit()


def get_recent_alerts() -> list[dict[str, str]]:
    """
    Retrieves recent alerts from the last 24 hours.
    """
    db: Session = SessionLocal()
    try:
        alerts = db.query(Alert).filter(Alert.date >= datetime.utcnow() - timedelta(days=1)).all()
        print(f"📝 Alerts fetched from DB: {alerts}")  # <-- Agregar esta línea para depurar
        return [
            {"symbol": alert.symbol, "date": alert.date.isoformat(), "message": alert.message}
            for alert in alerts
        ]
    finally:
        db.close()








