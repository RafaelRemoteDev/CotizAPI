import os
import sqlite3

# Ruta absoluta al archivo principal
DB_PATH = os.path.join(os.path.dirname(__file__), "cotizapi.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

