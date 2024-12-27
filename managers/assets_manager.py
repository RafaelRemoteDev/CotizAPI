from db.database import get_connection
import yfinance as yf

# Insertar un precio
def insertar_precio(simbolo, precio, fecha):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO activos (simbolo, fecha, precio)
        VALUES (?, ?, ?)
    ''', (simbolo.upper(), fecha, precio))
    conn.commit()
    conn.close()

# Obtener precio más reciente
def obtener_precio_reciente(simbolo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT precio, fecha FROM activos
        WHERE simbolo = ?
        ORDER BY fecha DESC LIMIT 1
    ''', (simbolo.upper(),))
    resultado = cursor.fetchone()
    conn.close()
    return resultado

# Obtener precio por fecha específica
def obtener_precio_por_fecha(simbolo, fecha):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT precio FROM activos
        WHERE simbolo = ? AND fecha = ?
    ''', (simbolo.upper(), fecha))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else None
from datetime import datetime
from services.yahoo_finance import obtener_precio_actual
from db.database import get_connection

def actualizar_precio_en_bd(simbolo):
    precio = obtener_precio_actual(simbolo)
    if precio:
        fecha = datetime.now().strftime('%Y-%m-%d')
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO activos (simbolo, fecha, precio)
            VALUES (?, ?, ?)
        ''', (simbolo.upper(), fecha, precio))
        conn.commit()
        conn.close()
        return precio
    else:
        print(f"No se pudo obtener el precio para {simbolo}.")
        return None
from managers.assets_manager import actualizar_precio_en_bd

def actualizar_todos_los_precios():
    activos = ["GC=F", "SI=F", "BTC-USD", "ZW=F", "CL=F"]  # Oro, Plata, Bitcoin, Trigo, Petróleo
    for simbolo in activos:
        precio = actualizar_precio_en_bd(simbolo)
        if precio:
            print(f"Actualizado: {simbolo} - Precio: {precio}")
        else:
            print(f"Error al actualizar {simbolo}.")

