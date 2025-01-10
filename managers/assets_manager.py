import yfinance as yf
from datetime import datetime
import sqlite3

# Ruta de la base de datos
DB_PATH = "cotizapi.db"

def get_connection():
    """Obtiene una conexión a la base de datos."""
    return sqlite3.connect(DB_PATH)

def obtener_precio_actual(simbolo):
    """
    Obtiene el precio actual de un activo desde Yahoo Finance.
    :param simbolo: Símbolo del activo (ej: "GC=F").
    :return: Precio actual del activo o None si ocurre un error.
    """
    try:
        ticker = yf.Ticker(simbolo)
        precio = ticker.history(period="1d")["Close"].iloc[-1]  # Precio de cierre más reciente
        return precio
    except Exception as e:
        print(f"Error al obtener el precio de {simbolo}: {e}")
        return None

def insertar_precio(simbolo, precio, fecha):
    """
    Inserta un precio en la base de datos.
    :param simbolo: Símbolo del activo (ej: "GC=F").
    :param precio: Precio del activo.
    :param fecha: Fecha en formato 'YYYY-MM-DD'.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO activos (simbolo, fecha, precio)
        VALUES (?, ?, ?)
    ''', (simbolo.upper(), fecha, precio))
    conn.commit()
    conn.close()

def actualizar_precio_en_bd(simbolo):
    """
    Actualiza el precio de un activo en la base de datos.
    :param simbolo: Símbolo del activo (ej: "GC=F").
    """
    precio = obtener_precio_actual(simbolo)
    if precio:
        fecha = datetime.now().strftime('%Y-%m-%d')
        insertar_precio(simbolo, precio, fecha)
        print(f"Actualizado: {simbolo} - Precio: {precio:.2f}")
    else:
        print(f"No se pudo obtener el precio para {simbolo}.")

def actualizar_todos_los_precios():
    """
    Actualiza los precios de todos los activos definidos.
    """
    activos = {
        "GC=F": "Oro 🥇",
        "SI=F": "Plata 🥈",
        "BTC-USD": "Bitcoin ₿",
        "ZW=F": "Trigo 🌾",
        "CL=F": "Petróleo 🛢️",
    }

    for simbolo, nombre in activos.items():
        print(f"Actualizando precio para {nombre} ({simbolo})...")
        actualizar_precio_en_bd(simbolo)

def obtener_precio_por_fecha(simbolo, fecha):
    """
    Obtiene el precio de un activo para una fecha específica desde la base de datos.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT precio FROM activos WHERE simbolo = ? AND fecha = ?",
        (simbolo.upper(), fecha),
    )
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else None

