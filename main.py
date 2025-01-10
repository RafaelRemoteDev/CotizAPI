import os
from datetime import datetime, timedelta

import uvicorn
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from managers.assets_manager import (
    obtener_precio_actual,
    actualizar_todos_los_precios,
    get_connection, obtener_precio_por_fecha
)
from fastapi import FastAPI
from api.endpoints import router as start_router
from api.endpoints import router as assets_router
from api.endpoints import router as daily_router
from api.endpoints import router as weekly_router
from api.endpoints import router as alerts_router

# Cargar variables de entorno
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

app = FastAPI()
@app.get("/")
def read_root():
    return {"¡CotizAPI está funcionando correctamente!  🤖💸🐂"}

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("El TOKEN del bot de Telegram no está configurado correctamente en el archivo .env")

# Comandos de Telegram
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando de inicio que muestra los comandos disponibles al usuario.
    """
    await update.message.reply_text(
        "¡Hola, soy CotizAPI! 🤖💸🐂\n"
        "Comandos disponibles:\n"
        "/assets - Ver precios actuales de los activos.\n"
        "/daily - Variación respecto al día anterior.\n"
        "/weekly - Variación respecto a la semana pasada.\n"
        "/update - Actualizar precios de los activos en la base de datos.\n"
        "/alerts - Ver las alertas generadas en las últimas 24 horas.\n"
    )



async def assets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando para mostrar los precios actuales de los activos.
    """
    activos = {
        "GC=F": "Oro 🥇",
        "SI=F": "Plata 🥈",
        "BTC-USD": "Bitcoin ₿",
        "ZW=F": "Trigo 🌾",
        "CL=F": "Petróleo 🛢️",
    }
    mensajes = []

    for simbolo, nombre in activos.items():
        precio = obtener_precio_actual(simbolo)
        if precio:
            mensajes.append(f"{nombre}: {precio:.2f} USD")
        else:
            mensajes.append(f"{nombre}: No se pudo obtener el precio.")

    await update.message.reply_text("\n".join(mensajes))


async def update_prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando para actualizar los precios de todos los activos en la base de datos.
    """
    await update.message.reply_text("⏳ Actualizando precios de los activos...")

    activos = {
        "GC=F": "Oro 🥇",
        "SI=F": "Plata 🥈",
        "BTC-USD": "Bitcoin ₿",
        "ZW=F": "Trigo 🌾",
        "CL=F": "Petróleo 🛢️",
    }

    for simbolo, nombre in activos.items():
        try:
            precio = obtener_precio_actual(simbolo)
            if precio:
                conn = get_connection()
                cursor = conn.cursor()
                fecha = datetime.now().strftime('%Y-%m-%d')
                cursor.execute(
                    "INSERT INTO activos (simbolo, fecha, precio) VALUES (?, ?, ?)",
                    (simbolo.upper(), fecha, precio),
                )
                conn.commit()
                conn.close()
                await update.message.reply_text(f"Actualizado: {nombre} - {precio:.2f} USD")
            else:
                await update.message.reply_text(f"No se pudo obtener el precio para {nombre}.")
        except Exception as e:
            await update.message.reply_text(f"Error al actualizar {nombre}: {e}")

    await update.message.reply_text("✅ Precios actualizados.")

async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando para mostrar la variación diaria de los activos.
    """
    activos = {
        "GC=F": "Oro 🥇",
        "SI=F": "Plata 🥈",
        "BTC-USD": "Bitcoin ₿",
        "ZW=F": "Trigo 🌾",
        "CL=F": "Petróleo 🛢️",
    }
    mensajes = []

    for simbolo, nombre in activos.items():
        precio_actual = obtener_precio_actual(simbolo)
        if precio_actual:
            fecha_ayer = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            precio_ayer = obtener_precio_por_fecha(simbolo, fecha_ayer)
            if precio_ayer:
                variacion = ((precio_actual - precio_ayer) / precio_ayer) * 100
                mensajes.append(f"{nombre}: Variación diaria {variacion:.2f}%")
            else:
                mensajes.append(f"{nombre}: No hay datos para el día anterior.")
        else:
            mensajes.append(f"{nombre}: No se pudo obtener el precio actual.")

    await update.message.reply_text("\n".join(mensajes))


async def weekly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando para mostrar la variación semanal de los activos.
    """
    activos = {
        "GC=F": "Oro 🥇",
        "SI=F": "Plata 🥈",
        "BTC-USD": "Bitcoin ₿",
        "ZW=F": "Trigo 🌾",
        "CL=F": "Petróleo 🛢️",
    }
    mensajes = []

    for simbolo, nombre in activos.items():
        precio_actual = obtener_precio_actual(simbolo)
        if precio_actual:
            fecha_hace_una_semana = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            precio_semana_pasada = obtener_precio_por_fecha(simbolo, fecha_hace_una_semana)
            if precio_semana_pasada:
                variacion = ((precio_actual - precio_semana_pasada) / precio_semana_pasada) * 100
                mensajes.append(f"{nombre}: Variación semanal {variacion:.2f}%")
            else:
                mensajes.append(f"{nombre}: No hay datos para hace 7 días.")
        else:
            mensajes.append(f"{nombre}: No se pudo obtener el precio actual.")

    await update.message.reply_text("\n".join(mensajes))
async def alertas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando para mostrar las alertas recientes (últimas 24 horas).
    """
    from managers.alerts_managers import obtener_alertas_recientes
    alertas = obtener_alertas_recientes()

    if not alertas:
        await update.message.reply_text("✅ No se han registrado alertas en las últimas 24 horas.")
        return

    mensajes = []
    for simbolo, fecha, mensaje in alertas:
        mensajes.append(f"🔔 {mensaje} (Fecha: {fecha})")

    await update.message.reply_text("\n".join(mensajes), parse_mode="HTML")


def main():
    """
    Función principal para ejecutar el bot de Telegram.
    """
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Registrar comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("assets", assets))
    application.add_handler(CommandHandler("update", update_prices))
    application.add_handler(CommandHandler("daily", daily))
    application.add_handler(CommandHandler("weekly", weekly))
    application.add_handler(CommandHandler("alerts", alertas))  # Nuevo comando


    print("El bot está en funcionamiento...")
    application.run_polling()

app.include_router(start_router, prefix="")
app.include_router(assets_router, prefix="")
app.include_router(daily_router, prefix="")
app.include_router(weekly_router, prefix="")
app.include_router(alerts_router, prefix="")


if __name__ == "__main__":
    # Asegurarse de que la base de datos está configurada antes de iniciar el bot
    print("⏳ Inicializando y actualizando precios de los activos en la base de datos...")
    actualizar_todos_los_precios()
    print("✅ Precios iniciales actualizados.")
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8032)
    # Iniciar el bot
    main()


