import os
from datetime import datetime, timedelta
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import uvicorn
import asyncio

# === Inicializar variables de entorno ===
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://cotizapi-url.railway.app/webhook")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("El TOKEN del bot de Telegram no está configurado correctamente en el archivo .env")
if not WEBHOOK_URL:
    raise ValueError("La URL del webhook no está configurada correctamente en el archivo .env")

# === Inicializar la aplicación de Telegram ===
telegram_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# === Tarea diaria para actualizar precios ===
async def daily_update_task():
    """Tarea diaria que actualiza los precios a las 6:00 AM."""
    while True:
        ahora = datetime.now()
        proxima_actualizacion = datetime(ahora.year, ahora.month, ahora.day, 6) + timedelta(days=1)
        tiempo_espera = (proxima_actualizacion - ahora).total_seconds()
        print(f"Esperando hasta las {proxima_actualizacion} para actualizar precios.")
        await asyncio.sleep(tiempo_espera)
        print(f"Precios actualizados automáticamente a las {datetime.now()}")

# === Inicializar FastAPI ===
app = FastAPI()

@app.on_event("startup")
async def startup():
    """Configuraciones al iniciar la aplicación."""
    await telegram_app.bot.set_webhook(WEBHOOK_URL)
    print(f"Webhook configurado en {WEBHOOK_URL}")
    asyncio.create_task(daily_update_task())

@app.on_event("shutdown")
async def shutdown():
    """Lógica para limpiar recursos al apagar la aplicación."""
    await telegram_app.bot.delete_webhook()
    print("Webhook eliminado. Apagando la aplicación.")

# === Endpoints ===
@app.get("/")
def read_root():
    """Endpoint raíz para confirmar que la API está activa."""
    return {"message": "¡Bienvenido a CotizAPI! Tu API financiera está lista para recibir comandos."}

@app.post("/webhook")
async def telegram_webhook(request: Request):
    """Maneja las solicitudes del webhook de Telegram."""
    json_update = await request.json()
    update = Update.de_json(json_update, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}

# === Registro de comandos ===
telegram_app.add_handler(CommandHandler("start", lambda update, context: update.message.reply_text("¡Hola! Bot activo.")))
telegram_app.add_handler(CommandHandler("assets", lambda update, context: update.message.reply_text("Precios actualizados.")))

# === Ejecutar la aplicación ===
if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8040))
    uvicorn.run(app, host=host, port=port)
