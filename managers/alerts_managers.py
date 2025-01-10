import sqlite3
from datetime import datetime
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
def generar_alertas():
    conn = get_connection()
    cursor = conn.cursor()

    # Consultar activos con variaciones significativas
    cursor.execute('''
        SELECT simbolo, fecha, variacion_diaria, variacion_semanal
        FROM activos
        WHERE variacion_diaria > 5 OR variacion_semanal > 10
    ''')
    resultados = cursor.fetchall()
    conn.close()

    for simbolo, fecha, variacion_diaria, variacion_semanal in resultados:
        mensaje = f"¡Alerta! {simbolo} ha tenido una variación "
        if variacion_diaria and variacion_diaria > 5:
            mensaje += f"diaria de {variacion_diaria:.2f}%. "
        if variacion_semanal and variacion_semanal > 10:
            mensaje += f"semanal de {variacion_semanal:.2f}%."

        insertar_alerta(simbolo, fecha, mensaje)
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


