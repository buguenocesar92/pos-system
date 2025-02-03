# sync.py

import datetime
from src.utils import request_with_refresh
from src.local_db import init_db, save_products

def sync_all_products():
    """
    Sincroniza TODOS los productos desde /products a la base local.
    Si la API está paginada, deberás iterar las páginas.
    """
    init_db()  # Asegurarnos de tener la tabla

    response = request_with_refresh("GET", "/products")
    if response.status_code == 200:
        data = response.json()
        items = data.get("items", [])  # Estructura: { 'items': [...], 'total': ... }
        save_products(items)
        print(f"Sincronizados {len(items)} productos a SQLite.")
    else:
        print(f"Error al sincronizar productos. Código: {response.status_code}")
