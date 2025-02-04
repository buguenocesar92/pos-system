# src/pos.py

import os
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QDialog, QLabel, QMessageBox, 
    QTableWidget, QSpinBox, QPushButton, QLineEdit, QComboBox, QAbstractItemView,
    QHeaderView, QTableWidgetItem, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from src.local_db import init_db, get_product_by_barcode
from src.sync import sync_all_products
from src.workers.sync_worker import SyncWorker
from src.workers.workers import WorkerThread

STYLE_SHEET = """
/* Estilos generales */
QWidget {
    background-color: #f9f9f9;
    font-family: Arial, sans-serif;
    font-size: 14px;
}

/* Botones */
QPushButton {
    background-color: #007bff; /* Azul por defecto */
    color: white;
    font-weight: bold;
    border-radius: 5px;
    padding: 10px;
}
QPushButton:hover {
    background-color: #0056b3;
}
QPushButton#CancelBtn {
    background-color: #dc3545;
}
QPushButton#CancelBtn:hover {
    background-color: #c82333;
}
QPushButton#ConfirmBtn {
    background-color: #28a745;
}
QPushButton#ConfirmBtn:hover {
    background-color: #218838;
}

/* Tabla */
QTableWidget {
    border: 1px solid #ccc;
    gridline-color: #ccc;
}
QTableWidget::item {
    padding: 5px;
}
QHeaderView::section {
    background-color: #f1f1f1;
    font-weight: bold;
    padding: 5px;
    border: none;
}
"""
# Diálogo de carga para registrar ventas
class LoadingDialog(QDialog):
    """Diálogo modal con un mensaje de carga."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Procesando...")
        self.setModal(True)
        self.setFixedSize(250, 100)
        layout = QHBoxLayout(self)
        self.label = QLabel("Registrando venta, por favor espere...")
        layout.addWidget(self.label)

class POSWindow(QWidget):
    """Ventana principal del POS, maneja la búsqueda de productos y su visualización."""
    
    SYNC_INTERVAL_MS = 1 * 60 * 1000  # 1 minuto (ajusta según lo necesario)

    def __init__(self):
        super().__init__()
        init_db()  # Crea/actualiza la base local

        self.setWindowTitle("Venta de Productos")
        self.showMaximized() 

        self.setStyleSheet(STYLE_SHEET)

        # 1) Construir la interfaz
        self._init_main_layout()

        # 3) Conectar eventos (definidos en pos_controller.py)
        self._connect_signals()

    def _init_main_layout(self):
        main_layout = QHBoxLayout(self)

        self.left_container = self._build_left_container()
        self.right_container = self._build_right_container()


        main_layout.addWidget(self.left_container, stretch=3)
        main_layout.addWidget(self.right_container, stretch=1)

        self.setLayout(main_layout)
    def _build_left_container(self) -> QFrame:
        """Crea el contenedor izquierdo con búsqueda y tabla de productos."""
        container = QFrame()
        layout = QVBoxLayout(container)

        # 🔹 Barra de búsqueda
        search_layout = QHBoxLayout()
        lbl_search = QLabel("Código del Producto:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Escanea o ingresa código...")
        self.btnBuscar = QPushButton("Buscar")
        self.btnSync = QPushButton("Sync")

        search_layout.addWidget(lbl_search)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.btnBuscar)
        search_layout.addWidget(self.btnSync)
        layout.addLayout(search_layout)

        # 🔹 Tabla de productos
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Código", "Descripción", "Precio", "Cantidad", "Acciones"])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

        return container

    def _build_right_container(self) -> QFrame:
        """Crea el contenedor derecho con totales y botones."""
        container = QFrame()
        layout = QVBoxLayout(container)

        # 🔹 Totales
        lbl_totales = QLabel("Totales")
        layout.addWidget(lbl_totales, alignment=Qt.AlignmentFlag.AlignLeft)
        self.label_total_amount = QLabel("Total: $0.00")
        layout.addWidget(self.label_total_amount, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addSpacing(20)

        # 🔹 Botones
        self.btn_confirmar_venta = QPushButton("CONFIRMAR VENTA")
        self.btn_cancelar_venta = QPushButton("CANCELAR VENTA")
        self.btn_cerrar_caja = QPushButton("CERRAR CAJA")

        layout.addWidget(self.btn_confirmar_venta)
        layout.addWidget(self.btn_cancelar_venta)
        layout.addWidget(self.btn_cerrar_caja)
        layout.addStretch()

        return container

    def _connect_signals(self):
        """Conecta los eventos de la UI con sus respectivos métodos."""
        self.search_input.returnPressed.connect(self.on_search_barcode)
        self.btnBuscar.clicked.connect(self.on_search_barcode)
        self.btnSync.clicked.connect(self.on_sync_products)
        self.btn_confirmar_venta.clicked.connect(self.on_confirmar_venta)
        self.btn_cancelar_venta.clicked.connect(self.on_cancelar_venta)
        self.btn_cerrar_caja.clicked.connect(self.on_cerrar_caja)

        # Auto-sync cada X tiempo
        self.timer = QTimer(self)
        self.timer.setInterval(self.SYNC_INTERVAL_MS)
        self.timer.timeout.connect(self.auto_sync)
        self.timer.start()

    # ----------------------------------------------------------------
    # Métodos de Lógica / Eventos
    # ----------------------------------------------------------------
    def on_search_barcode(self):
        """Maneja la búsqueda de un producto por código de barras."""
        barcode = self.search_input.text().strip()
        if not barcode:
            QMessageBox.warning(self, "Atención", "Ingresa un código de barras.")
            return

        product = get_product_by_barcode(barcode)
        if product:
            row_found = self.find_table_row_by_barcode(product["barcode"])
            if row_found is not None:
                self._increment_quantity_in_table(row_found)
            else:
                self.add_product_to_table(product)
        else:
            QMessageBox.information(
                self,
                "Sin resultados",
                f"No se encontró producto '{barcode}' en la base local."
            )

        self.search_input.clear()

    def on_sync_products(self):
        """Sincroniza manualmente los productos con la nube sin bloquear la UI."""
        self.sync_worker = SyncWorker()
        self.sync_worker.finished.connect(self.handle_sync_finished)
        self.sync_worker.start()

    def handle_sync_finished(self, result):
        """Maneja el resultado del hilo de sincronización."""
        if isinstance(result, Exception):
            print(f"Error en sincronización: {result}")
        else:
            print(result)

    def on_confirmar_venta(self):
        """Registra la venta usando un hilo para evitar congelar la UI."""
        items = []
        row_count = self.table.rowCount()

        for row in range(row_count):
            barcode_item = self.table.item(row, 0)
            if not barcode_item:
                continue

            barcode_str = barcode_item.text().strip()
            product_info = get_product_by_barcode(barcode_str)
            if not product_info or 'id' not in product_info:
                continue

            product_id = product_info['id']
            spin_widget = self.table.cellWidget(row, 3)
            quantity = spin_widget.value() if spin_widget else 1

            items.append({"product_id": product_id, "quantity": quantity})

        if not items:
            QMessageBox.warning(self, "Atención", "No hay productos para registrar la venta.")
            return

        self.loading_dialog = LoadingDialog(self)
        self.loading_dialog.show()

        self.worker = WorkerThread(payload={"items": items})
        self.worker.finished.connect(self.handle_finished)
        self.worker.start()

    def handle_finished(self, result):
        """Maneja la respuesta del hilo secundario para el registro de la venta."""
        self.loading_dialog.close()
        if isinstance(result, Exception):
            QMessageBox.critical(self, "Error", str(result))
            return

        response = result
        if response.status_code == 201:
            QMessageBox.information(self, "Venta Registrada", "Venta registrada con éxito.")
            self._clear_table_and_total()
        else:
            QMessageBox.critical(self, "Error al registrar venta", f"Código {response.status_code}:\n{response.text}")

    def auto_sync(self):
        """Sincroniza la base de datos local con la nube."""
        sync_all_products()
        print("Auto-sync completado.")

    def on_cancelar_venta(self):
        """Cancela la venta borrando los productos de la tabla, tras confirmación."""
        confirm = QMessageBox.question(
            self,
            "Cancelar Venta",
            "¿Estás seguro de que deseas cancelar la venta?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self._clear_table_and_total()
            QMessageBox.information(self, "Venta Cancelada", "La venta ha sido cancelada exitosamente.")

    # ----------------------------------------------------------------
    # Métodos de Apoyo
    # ----------------------------------------------------------------
    def add_product_to_table(self, product: dict):
        """Agrega un producto a la tabla."""
        row_idx = self.table.rowCount()
        self.table.insertRow(row_idx)

        barcode_str = str(product.get("barcode", ""))
        name_str = str(product.get("name", ""))
        price_val = float(product.get("unit_price", 0.0))

        self.table.setItem(row_idx, 0, QTableWidgetItem(barcode_str))
        self.table.setItem(row_idx, 1, QTableWidgetItem(name_str))
        self.table.setItem(row_idx, 2, QTableWidgetItem(f"${price_val:.2f}"))

        spin_cantidad = QSpinBox()
        spin_cantidad.setRange(1, 9999)
        spin_cantidad.setValue(1)
        spin_cantidad.valueChanged.connect(self.recalcular_total)
        self.table.setCellWidget(row_idx, 3, spin_cantidad)

        btn_delete = QPushButton("🗑")
        btn_delete.clicked.connect(lambda checked, r=row_idx: self.on_delete_item(r))
        self.table.setCellWidget(row_idx, 4, btn_delete)

        self.recalcular_total()

    def on_delete_item(self, row_idx: int):
        """Elimina un producto de la tabla."""
        self.table.removeRow(row_idx)
        self.recalcular_total()

    def recalcular_total(self):
        """Recalcula el total de la venta."""
        total = 0.0
        row_count = self.table.rowCount()
        for row in range(row_count):
            price_str = self.table.item(row, 2).text()
            price_val = float(price_str.replace("$", ""))
            spin = self.table.cellWidget(row, 3)
            quantity = spin.value() if spin else 1
            total += price_val * quantity
        self.label_total_amount.setText(f"Total: ${total:.2f}")

    def find_table_row_by_barcode(self, barcode: str) -> int | None:
        """Encuentra un producto en la tabla por código de barras."""
        for row in range(self.table.rowCount()):
            item_barcode = self.table.item(row, 0)
            if item_barcode and item_barcode.text() == barcode:
                return row
        return None

    def _increment_quantity_in_table(self, row_idx: int):
        spin = self.table.cellWidget(row_idx, 3)
        if spin:
            spin.setValue(spin.value() + 1)
        self.recalcular_total()

    def _clear_table_and_total(self):
        """Borra el contenido de la tabla, resetea el total y limpia el campo de búsqueda."""
        self.table.clearContents()
        self.table.setRowCount(0)
        self.label_total_amount.setText("Total: $0.00")
        self.search_input.clear()

    def on_cerrar_caja(self):
        """Abre la ventana de cierre de caja para ingresar el monto de cierre."""
        from .cierre_caja import CierreCajaWindow
        self.cierre_caja_window = CierreCajaWindow()
        self.cierre_caja_window.show()
