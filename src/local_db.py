# local_db.py

import sqlite3
import os
from constants import DB_FILE

def init_db():
    """
    Crea la tabla 'products' si no existe, con columna 'id' como PRIMARY KEY.
    Si ya existía una tabla sin 'id', deberás borrar o renombrar el DB_FILE
    para que se cree desde cero con la nueva estructura.
    """
    print("DEBUG: init_db() -> Creando tabla products con id INTEGER PRIMARY KEY.")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        barcode TEXT,
        name TEXT,
        unit_price REAL
    )
    """)
    conn.commit()
    conn.close()

def save_products(product_list):
    """
    Inserta o actualiza la lista de productos dada.
    Cada dict en 'product_list' debería ser algo como:
        {
          "id": 123,
          "barcode": "074312038228",
          "name": "Omega 3",
          "unit_price": 500.0
        }
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    for prod in product_list:
        product_id = prod.get("id")
        barcode    = prod.get("barcode", "")
        name       = prod.get("name", "")
        price      = float(prod.get("unit_price", 0.0))

        # Insert or replace => si existe 'id' igual, se actualiza
        cursor.execute("""
            INSERT OR REPLACE INTO products (id, barcode, name, unit_price)
            VALUES (?, ?, ?, ?)
        """, (product_id, barcode, name, price))

    conn.commit()
    conn.close()

def get_product_by_barcode(barcode: str):
    """
    Retorna un dict con { 'id': <int>, 'barcode': <str>, 'name': <str>, 'unit_price': <float> }
    o None si no existe en la base local.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT id, barcode, name, unit_price FROM products WHERE barcode = ?", (barcode,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0],
            "barcode": row[1],
            "name": row[2],
            "unit_price": row[3]
        }
    return None
