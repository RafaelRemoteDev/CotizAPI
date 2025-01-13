import yfinance as yf
from datetime import datetime
import sqlite3

# Ruta de la base de datos
DB_PATH = "cotizapi.db"


def inicializar_base_de_datos():
    """
    Crea la tabla 'activos' en la base de datos si no existe.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activos (
                simbolo TEXT NOT NULL,
                fecha TEXT NOT NULL,
                precio REAL NOT NULL,
                PRIMARY KEY (simbolo, fecha)
            )
        ''')
        conn.commit()
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")
    finally:
        conn.close()


def inicializar_modo_wal():
    """
    Activa el modo WAL (Write-Ahead Logging) para mejorar la concurrencia en la base de datos.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('PRAGMA journal_mode=WAL;')
        conn.commit()
    except Exception as e:
        print(f"Error al activar el modo WAL: {e}")
    finally:
        conn.close()


def get_connection():
    """
    Obtiene una conexión a la base de datos.
    """
    try:
        return sqlite3.connect(DB_PATH)
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")
        raise


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
    Inserta el precio de un activo en la base de datos o actualiza si ya existe.
    :param simbolo: Símbolo del activo.
    :param precio: Precio del activo.
    :param fecha: Fecha en formato 'YYYY-MM-DD'.
    """
    if precio is None or precio <= 0:
        print(f"Precio no válido para {simbolo}: {precio}")
        return

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO activos (simbolo, fecha, precio)
            VALUES (?, ?, ?)
            ON CONFLICT(simbolo, fecha) DO UPDATE SET
                precio = excluded.precio
        ''', (simbolo.upper(), fecha, precio))
        conn.commit()
        print(f"Insertado/Actualizado: {simbolo} - Precio: {precio:.2f} - Fecha: {fecha}")
    except Exception as e:
        print(f"Error al insertar/actualizar el precio para {simbolo}: {e}")
    finally:
        conn.close()



def actualizar_precio_en_bd(simbolo):
    """
    Obtiene y actualiza el precio de un activo en la base de datos.
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
    :param simbolo: Símbolo del activo.
    :param fecha: Fecha en formato 'YYYY-MM-DD'.
    :return: Precio del activo en esa fecha o None si no existe.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT precio FROM activos WHERE simbolo = ? AND fecha = ?",
            (simbolo.upper(), fecha),
        )
        resultado = cursor.fetchone()
        return resultado[0] if resultado else None
    except Exception as e:
        print(f"Error al obtener el precio para {simbolo} en la fecha {fecha}: {e}")
        return None
    finally:
        conn.close()


