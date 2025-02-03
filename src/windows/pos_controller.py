# windows/pos_controller.py

from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem, QPushButton
from PyQt6.QtCore import QTimer

from local_db import get_product_by_barcode, init_db
from sync import sync_all_products

def connect_signals(pos_window):
    """
    Conecta los botones y campos a los métodos de pos_window.
    pos_window es la instancia de POSWindow.
    """
    # Búsqueda manual o Enter
    pos_window.search_input.returnPressed.connect(pos_window.on_search_barcode)
    pos_window.btnBuscar.clicked.connect(pos_window.on_search_barcode)

    # Botón Sync
    pos_window.btnSync.clicked.connect(pos_window.on_sync_products)

    # Botón Confirmar Venta
    pos_window.btn_confirmar_venta.clicked.connect(pos_window.on_confirmar_venta)
    # Podrías conectar Cancelar, Cerrar Caja, etc.

    # Timer autsync
    pos_window.timer = QTimer(pos_window)
    pos_window.timer.setInterval(pos_window.SYNC_INTERVAL_MS)
    pos_window.timer.timeout.connect(pos_window.auto_sync)
    pos_window.timer.start()

