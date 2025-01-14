import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from managers.alerts_managers import obtener_alertas_recientes, generar_alertas
from managers.assets_manager import obtener_precio_actual, get_connection, obtener_precio_por_fecha

# Cargar variables de entorno
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("El TOKEN del bot de Telegram no está configurado correctamente en el archivo .env")

# Comandos del bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Muestra un mensaje de bienvenida y los comandos disponibles al usuario.
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
    Muestra los precios actuales de los activos.
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
        mensajes.append(f"{nombre}: {precio:.2f} USD" if precio else f"{nombre}: No se pudo obtener el precio.")
    await update.message.reply_text("\n".join(mensajes))

async def update_prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando para actualizar los precios de los activos y generar alertas.
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
        precio = obtener_precio_actual(simbolo)
        if precio:
            conn = get_connection()
            cursor = conn.cursor()
            fecha = datetime.now().strftime('%Y-%m-%d')
            try:
                # Inserción condicional para evitar conflictos
                cursor.execute('''
                    INSERT INTO activos (simbolo, fecha, precio)
                    VALUES (?, ?, ?)
                    ON CONFLICT(simbolo, fecha) DO UPDATE SET
                        precio = excluded.precio
                ''', (simbolo.upper(), fecha, precio))
                conn.commit()
                await update.message.reply_text(f"Actualizado: {nombre} - {precio:.2f} USD")
            except Exception as e:
                await update.message.reply_text(f"Error al actualizar {nombre}: {e}")
            finally:
                conn.close()
        else:
            await update.message.reply_text(f"No se pudo obtener el precio para {nombre}.")

    # Generar alertas después de actualizar los precios
    generar_alertas()

    await update.message.reply_text("✅ Precios actualizados y alertas generadas.")


async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Muestra la variación diaria de los precios de los activos.
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
    Muestra la variación semanal de los precios de los activos.
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

async def alerts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando para mostrar las alertas recientes (últimas 24 horas).
    """
    alertas = obtener_alertas_recientes()
    if not alertas:
        await update.message.reply_text("✅ No se han registrado alertas en las últimas 24 horas.")
        return

    # Incluir el símbolo del activo en cada mensaje
    mensajes = [f"🔔 ¡Alerta para {simbolo}! {mensaje} (Fecha: {fecha})" for simbolo, fecha, mensaje in alertas]
    await update.message.reply_text("\n".join(mensajes), parse_mode="HTML")


def main():
    """
    Inicializa el bot de Telegram y registra los comandos.
    """
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("assets", assets))
    application.add_handler(CommandHandler("update", update_prices))
    application.add_handler(CommandHandler("daily", daily))
    application.add_handler(CommandHandler("weekly", weekly))
    application.add_handler(CommandHandler("alerts", alerts))
    print("El bot está en funcionamiento...")
    application.run_polling()

