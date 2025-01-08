import asyncio
import sqlite3
from datetime import datetime

DB_PATH = "cotizapi.db"

async def send_alerts_task():
    while True:
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT simbolo, precio, fecha
                FROM activos
                WHERE fecha >= datetime('now', '-1 day')
            """)
            precios_recientes = cursor.fetchall()

            for simbolo, precio_actual, fecha_actual in precios_recientes:
                cursor.execute("""
                    SELECT precio
                    FROM activos
                    WHERE simbolo = ? AND fecha < ?
                    ORDER BY fecha DESC LIMIT 1
                """, (simbolo, fecha_actual))
                precio_anterior = cursor.fetchone()

                if precio_anterior:
                    variacion = abs((precio_actual - precio_anterior[0]) / precio_anterior[0])
                    if variacion > 0.05:
                        alerta = f"El activo {simbolo} ha variado más del 5%."
                        cursor.execute("""
                            INSERT INTO alertas (mensaje, fecha)
                            VALUES (?, ?)
                        """, (alerta, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                        print(f"Alerta generada: {alerta}")

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error en send_alerts_task: {e}")

        await asyncio.sleep(60)
