import sqlite3

import datetime
from fastapi import FastAPI, Request
from managers.assets_manager import obtener_precio_reciente, obtener_precio_por_fecha
from tasks.update_prices import update_prices_task
from tasks.send_alerts import send_alerts_task
from telegram import Update, Bot
from dotenv import load_dotenv
import os
import asyncio

# Cargar variables de entorno
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("El TOKEN del bot de Telegram no está configurado correctamente en el archivo .env")

bot = Bot(token=TELEGRAM_BOT_TOKEN)

# FastAPI app
app = FastAPI()

@app.get("/")
async def root():
    return {"Bienvenido a CotizAPI"}


@app.post("/webhook")
async def webhook(request: Request):
    """Endpoint que procesa las actualizaciones de Telegram."""
    data = await request.json()
    update = Update.de_json(data, bot)
    asyncio.create_task(process_update(update))
    return {"ok": True}

async def process_update(update: Update):
    """Procesa los comandos recibidos por Telegram."""
    chat_id = update.message.chat_id
    text = update.message.text

    if text == "/start":
        await bot.send_message(chat_id, (
            "¡Hola! Soy tu bot financiero. Estos son los comandos disponibles:\n"
            "/assets - Precio actual de los activos.\n"
            "/daily - Variación respecto al día anterior.\n"
            "/weekly - Variación respecto a la semana pasada.\n"
            "/alertas - Ver las alertas recientes."
        ))
    elif text == "/assets":
        await send_assets(chat_id)
    elif text == "/daily":
        await send_daily(chat_id)
    elif text == "/weekly":
        await send_weekly(chat_id)
    elif text == "/alertas":
        await send_alertas(chat_id)

async def send_assets(chat_id):
    """Muestra los precios actuales de los activos."""
    activos = ["GC=F", "SI=F", "BTC-USD", "ZW=F", "CL=F"]
    mensajes = []
    for simbolo in activos:
        precio_data = obtener_precio_reciente(simbolo)
        if precio_data:
            precio, fecha = precio_data
            mensajes.append(f"{simbolo}: {precio:.2f} USD (Última actualización: {fecha})")
        else:
            mensajes.append(f"{simbolo}: No se pudo obtener el precio.")
    await bot.send_message(chat_id, "\n".join(mensajes))

async def send_daily(chat_id):
    """Calcula la variación diaria de los activos."""
    activos = ["GC=F", "SI=F", "BTC-USD", "ZW=F", "CL=F"]
    mensajes = []
    for simbolo in activos:
        precio_actual = obtener_precio_reciente(simbolo)
        if precio_actual:
            fecha_ayer = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            precio_ayer = obtener_precio_por_fecha(simbolo, fecha_ayer)
            if precio_ayer:
                variacion = ((precio_actual[0] - precio_ayer) / precio_ayer) * 100
                mensajes.append(f"{simbolo}: Variación diaria {variacion:.2f}%")
            else:
                mensajes.append(f"{simbolo}: No hay datos del día anterior.")
        else:
            mensajes.append(f"{simbolo}: No hay datos disponibles.")
    await bot.send_message(chat_id, "\n".join(mensajes))

async def send_weekly(chat_id):
    """Calcula la variación semanal de los activos."""
    activos = ["GC=F", "SI=F", "BTC-USD", "ZW=F", "CL=F"]
    mensajes = []
    for simbolo in activos:
        precio_actual = obtener_precio_reciente(simbolo)
        if precio_actual:
            fecha_hace_una_semana = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            precio_semana_pasada = obtener_precio_por_fecha(simbolo, fecha_hace_una_semana)
            if precio_semana_pasada:
                variacion = ((precio_actual[0] - precio_semana_pasada) / precio_semana_pasada) * 100
                mensajes.append(f"{simbolo}: Variación semanal {variacion:.2f}%")
            else:
                mensajes.append(f"{simbolo}: No hay datos de hace una semana.")
        else:
            mensajes.append(f"{simbolo}: No hay datos disponibles.")
    await bot.send_message(chat_id, "\n".join(mensajes))

async def send_alertas(chat_id):
    """Consulta y envía las alertas recientes."""
    db_path = "cotizapi.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT mensaje, fecha 
        FROM alertas 
        WHERE fecha >= datetime('now', '-1 day')
    """)
    alertas = cursor.fetchall()
    conn.close()

    if not alertas:
        await bot.send_message(chat_id, "✅ No hay alertas recientes.")
    else:
        mensajes = "\n".join([f"{fecha} - {mensaje}" for mensaje, fecha in alertas])
        await bot.send_message(chat_id, f"🔔 Alertas recientes:\n\n{mensajes}")


# Iniciar el servidor
if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8032))



    print(f"🚀 Servidor iniciado en: http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)






