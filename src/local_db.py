# local_db.py

import sqlite3
import os
from constants import DB_FILE

def init_db():
    """
    Crea la tabla 'products' si no existe.
    Campos mínimos: barcode (PK), name, unit_price.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        barcode TEXT PRIMARY KEY,
        name TEXT,
        unit_price REAL
        -- Agrega más columnas si tu modelo de producto es más amplio
        -- Ej: brand TEXT, stock REAL, updated_at TEXT, etc.
    )
    """)
    conn.commit()
    conn.close()

def save_products(product_list):
    """
    Inserta o actualiza en la tabla 'products' la lista de productos dada.
    product_list: [
      { 'barcode': '11111', 'name': 'XYZ', 'unit_price': 10.0 },
      ...
    ]
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    for prod in product_list:
        barcode = prod.get("barcode")
        name = prod.get("name", "")
        price = prod.get("unit_price", 0.0)
        # Insert or replace => si existe un barcode igual, se actualiza
        cursor.execute("""
            INSERT OR REPLACE INTO products (barcode, name, unit_price)
            VALUES (?, ?, ?)
        """, (barcode, name, price))

    conn.commit()
    conn.close()

def get_product_by_barcode(barcode: str):
    """
    Retorna dict con { 'barcode': ..., 'name': ..., 'unit_price': ... }
    o None si no existe.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT barcode, name, unit_price FROM products WHERE barcode = ?", (barcode,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "barcode": row[0],
            "name": row[1],
            "unit_price": row[2]
        }
    else:
        return None
