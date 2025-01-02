import os
from datetime import datetime, timedelta
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import uvicorn

from managers.assets_manager import (
    obtener_precio_reciente,
    obtener_precio_por_fecha,
    actualizar_todos_los_precios,
)

# Inicializar FastAPI
app = FastAPI()

# Cargar variables de entorno
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("El TOKEN del bot de Telegram no está configurado correctamente en el archivo .env")

# Inicializar la aplicación de Telegram
telegram_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Webhook URL de Railway
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://cotizapi.railway.app/webhook")


# === Comandos de Telegram ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start: Mensaje de bienvenida."""
    await update.message.reply_text(
        "¡Hola! Soy tu bot financiero. Estos son los comandos disponibles:\n"
        "/assets - Precio actual de los activos.\n"
        "/daily - Variación respecto al día anterior.\n"
        "/weekly - Variación respecto a la semana pasada."
    )


async def assets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /assets: Obtiene los precios actuales."""
    activos = ["GC=F", "SI=F", "BTC-USD", "ZW=F", "CL=F"]  # Oro, Plata, Bitcoin, Trigo, Petróleo
    mensajes = []

    for simbolo in activos:
        precio = actualizar_todos_los_precios(simbolo)  # Actualiza el precio y lo obtiene
        if precio:
            mensajes.append(f"{simbolo}: {precio:.2f} USD")
        else:
            mensajes.append(f"{simbolo}: No se pudo obtener el precio.")

    await update.message.reply_text("\n".join(mensajes))


async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /daily: Variación diaria."""
    activos = ["oro", "plata", "bitcoin", "trigo", "petróleo"]
    mensajes = []

    for simbolo in activos:
        precio_actual = obtener_precio_reciente(simbolo.upper())
        if precio_actual:
            fecha_ayer = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            precio_ayer = obtener_precio_por_fecha(simbolo.upper(), fecha_ayer)
            if precio_ayer:
                variacion = ((precio_actual[0] - precio_ayer) / precio_ayer) * 100
                mensajes.append(f"{simbolo.capitalize()}: Variación diaria {variacion:.2f}%")
            else:
                mensajes.append(f"{simbolo.capitalize()}: No hay datos para el día anterior.")
        else:
            mensajes.append(f"{simbolo.capitalize()}: No hay datos disponibles.")
    await update.message.reply_text("\n".join(mensajes))


async def weekly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /weekly: Variación semanal."""
    activos = ["oro", "plata", "bitcoin", "trigo", "petróleo"]
    mensajes = []

    for simbolo in activos:
        precio_actual = obtener_precio_reciente(simbolo.upper())
        if precio_actual:
            fecha_semana_pasada = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            precio_semana_pasada = obtener_precio_por_fecha(simbolo.upper(), fecha_semana_pasada)
            if precio_semana_pasada:
                variacion = ((precio_actual[0] - precio_semana_pasada) / precio_semana_pasada) * 100
                mensajes.append(f"{simbolo.capitalize()}: Variación semanal {variacion:.2f}%")
            else:
                mensajes.append(f"{simbolo.capitalize()}: No hay datos para la semana pasada.")
        else:
            mensajes.append(f"{simbolo.capitalize()}: No hay datos disponibles.")
    await update.message.reply_text("\n".join(mensajes))


# === Configurar Telegram Webhook ===
@app.on_event("startup")
async def setup_webhook():
    """Configura el webhook para Telegram."""
    await telegram_app.bot.set_webhook(WEBHOOK_URL)
    print(f"Webhook configurado en {WEBHOOK_URL}")


@app.post("/webhook")
async def telegram_webhook(request: Request):
    """Maneja las solicitudes del webhook de Telegram."""
    json_update = await request.json()
    update = Update.de_json(json_update, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}


# === Endpoint para la API de actualización ===
@app.get("/update_prices")
async def update_prices():
    """Actualiza los precios manualmente."""
    actualizar_todos_los_precios()
    return {"message": "Precios actualizados correctamente."}


# === Actualización diaria programada (cron job) ===
@app.on_event("startup")
async def setup_daily_update():
    """Configura la tarea diaria para actualizar los precios."""
    import asyncio
    from datetime import timedelta

    async def daily_update_task():
        while True:
            ahora = datetime.now()
            # Calcula cuánto falta para las 6:00 AM del día siguiente
            proxima_actualizacion = datetime(ahora.year, ahora.month, ahora.day, 6) + timedelta(days=1)
            tiempo_espera = (proxima_actualizacion - ahora).total_seconds()
            print(f"Esperando hasta las {proxima_actualizacion} para actualizar precios.")
            await asyncio.sleep(tiempo_espera)
            actualizar_todos_los_precios()
            print(f"Precios actualizados automáticamente a las {datetime.now()}")

    asyncio.create_task(daily_update_task())


# === Ejecutar la aplicación ===
if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8040))
    uvicorn.run(app, host=host, port=port)
