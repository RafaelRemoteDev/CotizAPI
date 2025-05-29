from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from loguru import logger
from db.database import SessionLocal, Alert
from managers.assets_manager import calculate_variations
from config import ASSETS

# Alert thresholds defined directly here
DAILY_THRESHOLD = 3.0    # 3% daily variation
WEEKLY_THRESHOLD = 5.0   # 5% weekly variation
MONTHLY_THRESHOLD = 7.0  # 7% monthly variation


def generate_alerts() -> None:
    """
    Generates alerts based on price variations exceeding predefined thresholds.
    Alerts are always stored in the database.

    Returns:
    -------
        None
    """
    db: Session = SessionLocal()
    try:
        # Calculate variations
        daily_variations = calculate_variations(ASSETS, 1)
        weekly_variations = calculate_variations(ASSETS, 7)
        monthly_variations = calculate_variations(ASSETS, 30)

        alerts_generated = False

        for asset in ASSETS:
            # Check daily variation (threshold: 3%)
            daily_variation = next(
                (item["variation"] for item in daily_variations if item["symbol"] == asset), None
            )

            if daily_variation is not None and abs(daily_variation) > DAILY_THRESHOLD:
                direction = "increase" if daily_variation > 0 else "decrease"
                message = f"Daily {direction} of {daily_variation:.2f}% exceeded the {DAILY_THRESHOLD}% threshold!"
                insert_alert(db, asset, message)
                alerts_generated = True
                logger.warning(f"DAILY ALERT: {asset} - {message}")

            # Check weekly variation (threshold: 5%)
            weekly_variation = next(
                (item["variation"] for item in weekly_variations if item["symbol"] == asset), None
            )

            if weekly_variation is not None and abs(weekly_variation) > WEEKLY_THRESHOLD:
                direction = "increase" if weekly_variation > 0 else "decrease"
                message = f"Weekly {direction} of {weekly_variation:.2f}% exceeded the {WEEKLY_THRESHOLD}% threshold!"
                insert_alert(db, asset, message)
                alerts_generated = True
                logger.warning(f"WEEKLY ALERT: {asset} - {message}")

            # Check monthly variation (threshold: 7%)
            monthly_variation = next(
                (item["variation"] for item in monthly_variations if item["symbol"] == asset), None
            )

            if monthly_variation is not None and abs(monthly_variation) > MONTHLY_THRESHOLD:
                direction = "increase" if monthly_variation > 0 else "decrease"
                message = f"Monthly {direction} of {monthly_variation:.2f}% exceeded the {MONTHLY_THRESHOLD}% threshold!"
                insert_alert(db, asset, message)
                alerts_generated = True
                logger.warning(f"MONTHLY ALERT: {asset} - {message}")

        if alerts_generated:
            logger.info("Alerts generated and stored in database")
        else:
            logger.info("No significant variations detected. Current thresholds: "
                       f"Daily >{DAILY_THRESHOLD}%, Weekly >{WEEKLY_THRESHOLD}%, Monthly >{MONTHLY_THRESHOLD}%")

    except Exception as e:
        logger.error(f"Error generating alerts: {e}")
    finally:
        db.close()


def insert_alert(db: Session, symbol: str, message: str) -> None:
    """
    Inserts a new alert into the database.

    Args:
    ----
        db: Database session.
        symbol: Asset symbol.
        message: Alert message.

    Returns:
    -------
        None
    """
    try:
        logger.info(f"Inserting alert -> Symbol: {symbol} | Message: {message}")

        # Save to database
        new_alert = Alert(symbol=symbol, date=datetime.now(timezone.utc), message=message)
        db.add(new_alert)
        db.commit()

        logger.info(f"Alert successfully stored in database for {symbol}")

    except Exception as e:
        logger.error(f"Error inserting alert for {symbol}: {e}")
        db.rollback()


def get_recent_alerts() -> list[dict[str, str]]:
    """
    Retrieves recent alerts from the last 24 hours.

    Returns:
    -------
        List of dictionaries containing alert information.
    """
    db: Session = SessionLocal()
    try:
        one_day_ago = datetime.now(timezone.utc) - timedelta(days=1)
        alerts = db.query(Alert).filter(Alert.date >= one_day_ago).all()
        logger.debug(f"Alerts fetched from DB: {len(alerts)}")

        return [
            {"symbol": alert.symbol, "date": alert.date.isoformat(), "message": alert.message}
            for alert in alerts
        ]
    except Exception as e:
        logger.error(f"Error fetching recent alerts: {e}")
        return []
    finally:
        db.close()


def check_and_log_current_variations() -> None:
    """
    Helper function to check current variations and debug.
    """
    try:
        daily_variations = calculate_variations(ASSETS, 1)
        weekly_variations = calculate_variations(ASSETS, 7)
        monthly_variations = calculate_variations(ASSETS, 30)

        logger.info("=== CURRENT VARIATIONS ===")
        for asset in ASSETS:
            daily = next((item["variation"] for item in daily_variations if item["symbol"] == asset), None)
            weekly = next((item["variation"] for item in weekly_variations if item["symbol"] == asset), None)
            monthly = next((item["variation"] for item in monthly_variations if item["symbol"] == asset), None)

            daily_str = f"{daily:+.2f}%" if daily is not None else "N/A"
            weekly_str = f"{weekly:+.2f}%" if weekly is not None else "N/A"
            monthly_str = f"{monthly:+.2f}%" if monthly is not None else "N/A"

            # Indicate if they exceed thresholds
            daily_alert = "ALERT!" if daily is not None and abs(daily) > DAILY_THRESHOLD else ""
            weekly_alert = "ALERT!" if weekly is not None and abs(weekly) > WEEKLY_THRESHOLD else ""
            monthly_alert = "ALERT!" if monthly is not None and abs(monthly) > MONTHLY_THRESHOLD else ""

            logger.info(f"{asset}: Daily {daily_str} {daily_alert}, Weekly {weekly_str} {weekly_alert}, Monthly {monthly_str} {monthly_alert}")

        logger.info(f"Thresholds: Daily >{DAILY_THRESHOLD}%, Weekly >{WEEKLY_THRESHOLD}%, Monthly >{MONTHLY_THRESHOLD}%")

    except Exception as e:
        logger.error(f"Error checking current variations: {e}")