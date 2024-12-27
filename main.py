import os
from datetime import datetime, timedelta

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from managers.assets_manager import obtener_precio_reciente, obtener_precio_por_fecha, actualizar_precio_en_bd, \
    actualizar_todos_los_precios

app = FastAPI()

# Cargar las variables de entorno desde el archivo .env
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("El TOKEN del bot de Telegram no está configurado correctamente en el archivo .env")

@app.get("/")
def read_root():
    return {"Bienvenido a CotizAPI"}

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "¡Hola! Soy tu bot financiero. Estos son los comandos disponibles:\n"
        "/assets - Precio actual de los activos.\n"
        "/daily - Variación respecto al día anterior.\n"
        "/weekly - Variación respecto a la semana pasada."
    )


# Comando /assets
async def assets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    activos = ["GC=F", "SI=F", "BTC-USD", "ZW=F", "CL=F"]  # Símbolos para Oro, Plata, Bitcoin, Trigo, Petróleo
    mensajes = []

    for simbolo in activos:
        precio = actualizar_precio_en_bd(simbolo)
        if precio:
            mensajes.append(f"{simbolo}: {precio:.2f} USD")
        else:
            mensajes.append(f"{simbolo}: No se pudo obtener el precio.")

    await update.message.reply_text("\n".join(mensajes))


async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
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


from apscheduler.schedulers.background import BackgroundScheduler

def iniciar_tareas_periodicas():
    scheduler = BackgroundScheduler()
    scheduler.add_job(actualizar_todos_los_precios, "interval", hours=1)  # Ejecuta cada 1 hora
    scheduler.start()
    print("Tarea periódica configurada para actualizar los precios.")


# Configuración principal del bot
def main():
    # Crear la aplicación del bot
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Agregar manejadores de comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("assets", assets))
    application.add_handler(CommandHandler("daily", daily))
    application.add_handler(CommandHandler("weekly", weekly))

    # Iniciar el bot
    print("El bot está en funcionamiento...")
    application.run_polling()


if __name__ == "__main__":
    # Configuración del host y puerto
    host = "192.168.1.42"  # Cambia por tu IP si es necesario
    port = 8000

    # Arranca el servidor Uvicorn
    uvicorn.run("main:app", host=host, port=port, reload=True)
