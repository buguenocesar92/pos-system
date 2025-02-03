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
    # Conectar búsqueda manual o al presionar Enter
    pos_window.search_input.returnPressed.connect(pos_window.on_search_barcode)
    pos_window.btnBuscar.clicked.connect(pos_window.on_search_barcode)

    # Botón Sync
    pos_window.btnSync.clicked.connect(pos_window.on_sync_products)

    # Botón Confirmar Venta
    pos_window.btn_confirmar_venta.clicked.connect(pos_window.on_confirmar_venta)

    # Botón Cancelar Venta
    pos_window.btn_cancelar_venta.clicked.connect(pos_window.on_cancelar_venta)

    # Botón Cerrar Caja: al hacer clic, se invoca el método on_cerrar_caja,
    # el cual debe abrir la ventana de cierre de caja (similar a la de apertura) que
    # envía el parámetro closing_amount a la API.
    pos_window.btn_cerrar_caja.clicked.connect(pos_window.on_cerrar_caja)

    # Timer para autosincronización
    pos_window.timer = QTimer(pos_window)
    pos_window.timer.setInterval(pos_window.SYNC_INTERVAL_MS)
    pos_window.timer.timeout.connect(pos_window.auto_sync)
    pos_window.timer.start()
