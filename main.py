import os
from datetime import datetime, timedelta
from fastapi import FastAPI
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import uvicorn

from managers.assets_manager import (
    obtener_precio_reciente,
    obtener_precio_por_fecha,
    actualizar_precio_en_bd,
    actualizar_todos_los_precios,
)

app = FastAPI()

# Cargar las variables de entorno desde el archivo .env
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("El TOKEN del bot de Telegram no está configurado correctamente en el archivo .env")


@app.get("/")
def read_root():
    return {"Bienvenido a CotizAPI"}


# Comandos de Telegram
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "¡Hola! Soy tu bot financiero. Estos son los comandos disponibles:\n"
        "/assets - Precio actual de los activos.\n"
        "/daily - Variación respecto al día anterior.\n"
        "/weekly - Variación respecto a la semana pasada."
    )


async def assets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    activos = ["GC=F", "SI=F", "BTC-USD", "ZW=F", "CL=F"]  # Oro, Plata, Bitcoin, Trigo, Petróleo
    mensajes = []

    for simbolo in activos:
        precio = actualizar_precio_en_bd(simbolo)
        if precio:
            mensajes.append(f"{simbolo}: {precio:.2f} USD")
        else:
            mensajes.append(f"{simbolo}: No se pudo obtener el precio.")

    await update.message.reply_text("\n".join(mensajes))


async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Mapeo entre nombres comunes y símbolos de la base de datos
    activos_map = {
        "oro": "GC=F",
        "plata": "SI=F",
        "bitcoin": "BTC-USD",
        "trigo": "ZW=F",
        "petróleo": "CL=F"
    }

    # Activos que deseas procesar
    activos = ["oro", "plata", "bitcoin", "trigo", "petróleo"]
    mensajes = []

    # Procesar cada activo
    for simbolo in activos:
        # Convertir el nombre común al símbolo en la base de datos
        simbolo_db = activos_map[simbolo]

        # Obtener el precio actual desde la base de datos
        precio_actual = obtener_precio_reciente(simbolo_db)

        if precio_actual:
            fecha_ayer = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            precio_ayer = obtener_precio_por_fecha(simbolo_db, fecha_ayer)
            if precio_ayer:
                variación = ((precio_actual[0] - precio_ayer) / precio_ayer) * 100
                mensajes.append(f"{simbolo.capitalize()}: Variación diaria {variación:.2f}%")
            else:
                mensajes.append(f"{simbolo.capitalize()}: No hay datos para el día anterior.")
        else:
            mensajes.append(f"{simbolo.capitalize()}: No hay datos disponibles.")

    # Responder al usuario con los mensajes generados
    await update.message.reply_text("\n".join(mensajes))


async def weekly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Mapeo entre nombres comunes y símbolos en la base de datos
    activos_map = {
        "oro": "GC=F",
        "plata": "SI=F",
        "bitcoin": "BTC-USD",
        "trigo": "ZW=F",
        "petróleo": "CL=F"
    }

    # Activos a procesar
    activos = ["oro", "plata", "bitcoin", "trigo", "petróleo"]
    mensajes = []

    # Procesar cada activo
    for simbolo in activos:
        simbolo_db = activos_map[simbolo]

        # Obtener el precio actual desde la base de datos
        precio_actual = obtener_precio_reciente(simbolo_db)

        if precio_actual:
            # Obtener la fecha de hace 7 días
            fecha_hace_una_semana = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            precio_semana_pasada = obtener_precio_por_fecha(simbolo_db, fecha_hace_una_semana)

            if precio_semana_pasada:
                variacion = ((precio_actual[0] - precio_semana_pasada) / precio_semana_pasada) * 100
                mensajes.append(f"{simbolo.capitalize()}: Variación semanal {variacion:.2f}%")
            else:
                # Si no hay datos para hace 7 días
                mensajes.append(f"{simbolo.capitalize()}: No hay datos para hace 7 días.")
        else:
            # Si no hay datos recientes
            mensajes.append(f"{simbolo.capitalize()}: No hay datos disponibles.")

    # Responder con los resultados
    await update.message.reply_text("\n".join(mensajes))


def main():
    # Crear la aplicación del bot de Telegram
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Agregar manejadores de comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("assets", assets))
    application.add_handler(CommandHandler("daily", daily))
    application.add_handler(CommandHandler("weekly", weekly))

    # Ejecutar el bot en el mismo bucle de eventos principal
    print("El bot está en funcionamiento...")
    application.run_polling()


if __name__ == "__main__":
    # Ejecutar FastAPI y Telegram en el mismo proceso
    from multiprocessing import Process

    # Ejecutar el bot en un proceso separado
    bot_process = Process(target=main)
    bot_process.start()

    # Ejecutar FastAPI
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8040))
    uvicorn.run(app, host=host, port=port)

    # Esperar al proceso del bot
    bot_process.join()