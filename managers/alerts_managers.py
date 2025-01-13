import sqlite3
from datetime import datetime

import timedelta

from managers.assets_manager import get_connection

# Ruta de la base de datos
DB_PATH = "cotizapi.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

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



# Insertar una alerta en la tabla 'alertas'
def insertar_alerta(simbolo, fecha, mensaje):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO alertas (simbolo, fecha, mensaje)
        VALUES (?, ?, ?)
    ''', (simbolo.upper(), fecha, mensaje))

    conn.commit()
    conn.close()


# Generar alertas en función de las variaciones
from datetime import datetime, timedelta

def generar_alertas():
    activos = ["GC=F", "SI=F", "BTC-USD", "ZW=F", "CL=F"]
    fecha_actual = datetime.now().strftime('%Y-%m-%d')

    for simbolo in activos:
        # Obtener precios recientes y de fechas específicas
        precio_reciente = obtener_precio_reciente(simbolo)
        if not precio_reciente:
            continue

        precio_hace_un_dia = obtener_precio_por_fecha(simbolo, (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'))
        precio_hace_una_semana = obtener_precio_por_fecha(simbolo, (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'))

        mensaje = ""
        # Calcular variación diaria
        if precio_hace_un_dia:
            variacion_diaria = ((precio_reciente[0] - precio_hace_un_dia) / precio_hace_un_dia) * 100
            if abs(variacion_diaria) > 3:  # Umbral de alerta diaria
                mensaje += f"Variación diaria de {variacion_diaria:.2f}%. "

        # Calcular variación semanal
        if precio_hace_una_semana:
            variacion_semanal = ((precio_reciente[0] - precio_hace_una_semana) / precio_hace_una_semana) * 100
            if abs(variacion_semanal) > 6:  # Umbral de alerta semanal
                mensaje += f"Variación semanal de {variacion_semanal:.2f}%. "

        # Generar alerta si hay mensaje
        if mensaje:
            insertar_alerta(simbolo, fecha_actual, f"¡Alerta! {mensaje}")
            print(f"Alerta generada para {simbolo}: {mensaje}")

# Obtener alertas recientes (últimas 24 horas)
def obtener_alertas_recientes():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT simbolo, fecha, mensaje
        FROM alertas
        WHERE fecha >= datetime('now', '-1 day')
    ''')
    alertas = cursor.fetchall()
    conn.close()
    return alertas


