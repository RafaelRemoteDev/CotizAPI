import os
import sqlite3
from datetime import datetime, timedelta
from fastapi import FastAPI
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import uvicorn
from telegram.error import Conflict

from managers.assets_manager import (
    obtener_precio_reciente,
    obtener_precio_por_fecha,
)

# Configuración de FastAPI
app = FastAPI()

# Cargar variables de entorno
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("El TOKEN del bot de Telegram no está configurado correctamente en el archivo .env")

@app.get("/")
def read_root():
    return {"Bienvenido a CotizAPI! 🤖💸🐂"}

# Comandos de Telegram
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(
            "¡Hola, soy CotizAPI, tu bot financiero!🤖💸🐂\n "
            "Estos son tus comandos disponibles:\n"
            "/assets - Precio actual de los activos.\n"
            "/daily - Variación respecto al día anterior.\n"
            "/weekly - Variación respecto a la semana pasada.\n"
            "/alertas - Alertas recientes."
        )
    except Exception as e:
        print(f" Error en /start: {e}")

async def assets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        activos = {
            "GC=F": "Oro 🥇",
            "SI=F": "Plata 🥈",
            "BTC-USD": "Bitcoin 🪙",
            "ZW=F": "Trigo 🌾",
            "CL=F": "Petróleo 🛢️",
        }
        mensajes = []

        for simbolo, nombre in activos.items():
            precio_data = obtener_precio_reciente(simbolo)
            if precio_data:
                precio = precio_data[0] if isinstance(precio_data, tuple) else precio_data
                mensajes.append(f"{nombre}: {precio:.2f} $")
            else:
                mensajes.append(f"{nombre}: No se pudo obtener el precio.")

        await update.message.reply_text("\n".join(mensajes))
    except Exception as e:
        print(f"❌ Error en /assets: {e}")
        await update.message.reply_text("❌ Error al procesar el comando /assets.")

async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        activos_map = {
            "oro 🥇": "GC=F",
            "plata 🥈": "SI=F",
            "bitcoin 🪙": "BTC-USD",
            "trigo 🌾": "ZW=F",
            "petróleo 🛢️": "CL=F",
        }

        mensajes = []
        for nombre, simbolo_db in activos_map.items():
            precio_actual = obtener_precio_reciente(simbolo_db)
            if precio_actual:
                fecha_ayer = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                precio_ayer = obtener_precio_por_fecha(simbolo_db, fecha_ayer)
                if precio_ayer:
                    variacion = ((precio_actual[0] - precio_ayer) / precio_ayer) * 100
                    mensajes.append(f"{nombre.capitalize()}: Variación diaria {variacion:.2f}%")
                else:
                    mensajes.append(f"{nombre.capitalize()}: No hay datos para el día anterior.")
            else:
                mensajes.append(f"{nombre.capitalize()}: No hay datos disponibles.")
        await update.message.reply_text("\n".join(mensajes))
    except Exception as e:
        print(f"❌ Error en /daily: {e}")
        await update.message.reply_text("❌ Error al procesar el comando /daily.")

async def weekly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        activos_map = {
            "oro 🥇": "GC=F",
            "plata 🥈": "SI=F",
            "bitcoin 🪙": "BTC-USD",
            "trigo 🌾": "ZW=F",
            "petróleo 🛢️": "CL=F",
        }

        mensajes = []
        for nombre, simbolo_db in activos_map.items():
            precio_actual = obtener_precio_reciente(simbolo_db)
            if precio_actual:
                fecha_hace_una_semana = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                precio_semana_pasada = obtener_precio_por_fecha(simbolo_db, fecha_hace_una_semana)
                if precio_semana_pasada:
                    variacion = ((precio_actual[0] - precio_semana_pasada) / precio_semana_pasada) * 100
                    mensajes.append(f"{nombre.capitalize()}: Variación semanal {variacion:.2f}%")
                else:
                    mensajes.append(f"{nombre.capitalize()}: No hay datos para hace 7 días.")
            else:
                mensajes.append(f"{nombre.capitalize()}: No hay datos disponibles.")
        await update.message.reply_text("\n".join(mensajes))
    except Exception as e:
        print(f"❌ Error en /weekly: {e}")
        await update.message.reply_text("❌ Error al procesar el comando /weekly.")

async def alertas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db_path = "C:/Users/Usuario/PycharmProjects/cotizAPI/cotizapi.db"
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT mensaje 
            FROM alertas 
            WHERE fecha >= datetime('now', '-1 day')
        """)
        alertas = cursor.fetchall()

        if not alertas:
            await update.message.reply_text("✅ No hay alertas recientes.")
        else:
            mensajes = "\n\n".join([alerta[0] for alerta in alertas])
            await update.message.reply_text(
                f"🔔 <b>Alertas recientes:</b>\n\n{mensajes}",
                parse_mode="HTML"
            )
    except sqlite3.Error as e:
        print(f"❌ Error al acceder a las alertas: {e}")
        await update.message.reply_text("❌ Error al procesar las alertas.")
    finally:
        if conn:
            conn.close()

# Función principal
def main():
    try:
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("assets", assets))
        application.add_handler(CommandHandler("daily", daily))
        application.add_handler(CommandHandler("weekly", weekly))
        application.add_handler(CommandHandler("alertas", alertas))

        print("El bot está en funcionamiento...")
        application.run_polling()
    except Conflict:
        print("❌ El bot ya está siendo ejecutado en otro proceso. Detén otros procesos antes de iniciar.")

if __name__ == "__main__":
    from multiprocessing import Process

    bot_process = Process(target=main)
    bot_process.start()

    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8020))
    uvicorn.run(app, host=host, port=port)

    bot_process.join()






