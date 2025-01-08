import asyncio
import sqlite3
from datetime import datetime
from managers.assets_manager import fetch_external_prices

DB_PATH = "cotizapi.db"

async def update_prices_task():
    while True:
        try:
            new_prices = fetch_external_prices()

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            for simbolo, precio in new_prices.items():
                if precio:
                    cursor.execute("""
                        INSERT INTO activos (simbolo, fecha, precio)
                        VALUES (?, ?, ?)
                    """, (simbolo, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), precio))
            conn.commit()
            conn.close()

            print("Precios actualizados correctamente:", new_prices)
        except Exception as e:
            print(f"Error en update_prices_task: {e}")

        await asyncio.sleep(3600)
