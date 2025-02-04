# src/pos_window.py

import os
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QTableWidgetItem
from PyQt6.QtCore import QTimer
from src.local_db import init_db, get_product_by_barcode
from src.sync import sync_all_products
from src.workers.sync_worker import SyncWorker
from src.workers.workers import WorkerThread
from src.components.left_panel import LeftPanel
from src.components.right_panel import RightPanel
from src.components.loading_dialog import LoadingDialog

def load_stylesheet(file_path: str) -> str:
    """Carga y retorna el contenido del archivo de estilos."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

class POSWindow(QWidget):
    """Ventana principal del POS que integra el panel izquierdo y derecho."""
    SYNC_INTERVAL_MS = 1 * 60 * 1000  # 1 minuto

    def __init__(self):
        super().__init__()
        init_db()  # Inicializa la base local

        self.setWindowTitle("Venta de Productos")
        self.showMaximized()

        # Cargar estilos desde un archivo externo (ajusta la ruta según tu estructura)
        stylesheet_path = os.path.join(os.path.dirname(__file__), "style.qss")
        self.setStyleSheet(load_stylesheet(stylesheet_path))

        self._init_ui()
        self._connect_signals()
        QTimer.singleShot(200, self.set_search_focus)

    def set_search_focus(self):
        self.left_panel.search_input.setFocus()

    def _init_ui(self):
        main_layout = QHBoxLayout(self)
        self.left_panel = LeftPanel(self)
        self.right_panel = RightPanel(self)
        main_layout.addWidget(self.left_panel, stretch=3)
        main_layout.addWidget(self.right_panel, stretch=1)
        self.setLayout(main_layout)

    def _connect_signals(self):
        # Conectar señales del LeftPanel
        self.left_panel.search_input.returnPressed.connect(self.on_search_barcode)
        self.left_panel.btnBuscar.clicked.connect(self.on_search_barcode)
        self.left_panel.btnSync.clicked.connect(self.on_sync_products)
        # Conectar señales del RightPanel
        self.right_panel.btn_confirmar_venta.clicked.connect(self.on_confirmar_venta)
        self.right_panel.btn_cancelar_venta.clicked.connect(self.on_cancelar_venta)
        self.right_panel.btn_cerrar_caja.clicked.connect(self.on_cerrar_caja)
        # Auto-sync
        self.timer = QTimer(self)
        self.timer.setInterval(self.SYNC_INTERVAL_MS)
        self.timer.timeout.connect(self.auto_sync)
        self.timer.start()

    # Métodos de lógica y eventos (la implementación es similar a la original)
    def on_search_barcode(self):
        barcode = self.left_panel.search_input.text().strip()
        if not barcode:
            from PyQt6.QtWidgets import QMessageBox
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
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(
                self, "Sin resultados",
                f"No se encontró producto '{barcode}' en la base local."
            )
        self.left_panel.search_input.clear()

    def on_sync_products(self):
        self.sync_worker = SyncWorker()
        self.sync_worker.finished.connect(self.handle_sync_finished)
        self.sync_worker.start()

    def handle_sync_finished(self, result):
        if isinstance(result, Exception):
            print(f"Error en sincronización: {result}")
        else:
            print(result)

    def on_confirmar_venta(self):
        from PyQt6.QtWidgets import QMessageBox
        items = []
        row_count = self.left_panel.table.rowCount()
        for row in range(row_count):
            barcode_item = self.left_panel.table.item(row, 0)
            if not barcode_item:
                continue
            barcode_str = barcode_item.text().strip()
            product_info = get_product_by_barcode(barcode_str)
            if not product_info or 'id' not in product_info:
                continue
            product_id = product_info['id']
            spin_widget = self.left_panel.table.cellWidget(row, 3)
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
        from PyQt6.QtWidgets import QMessageBox
        self.loading_dialog.close()
        if isinstance(result, Exception):
            QMessageBox.critical(self, "Error", str(result))
            return
        response = result
        if response.status_code == 201:
            QMessageBox.information(self, "Venta Registrada", "Venta registrada con éxito.")
            self._clear_table_and_total()
        else:
            QMessageBox.critical(
                self, "Error al registrar venta",
                f"Código {response.status_code}:\n{response.text}"
            )

    def auto_sync(self):
        sync_all_products()
        print("Auto-sync completado.")

    def on_cancelar_venta(self):
        from PyQt6.QtWidgets import QMessageBox
        confirm = QMessageBox.question(
            self, "Cancelar Venta",
            "¿Estás seguro de que deseas cancelar la venta?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self._clear_table_and_total()
            QMessageBox.information(self, "Venta Cancelada", "La venta ha sido cancelada exitosamente.")

    def on_cerrar_caja(self):
        from src.views.cierre_caja import CierreCajaWindow
        self.cierre_caja_window = CierreCajaWindow()
        self.cierre_caja_window.show()

    # Métodos de apoyo para manipular la tabla
    def add_product_to_table(self, product: dict):
        row_idx = self.left_panel.table.rowCount()
        self.left_panel.table.insertRow(row_idx)

        barcode_str = str(product.get("barcode", ""))
        name_str = str(product.get("name", ""))
        price_val = float(product.get("unit_price", 0.0))

        self.left_panel.table.setItem(row_idx, 0, QTableWidgetItem(barcode_str))
        self.left_panel.table.setItem(row_idx, 1, QTableWidgetItem(name_str))
        self.left_panel.table.setItem(row_idx, 2, QTableWidgetItem(f"${price_val:.2f}"))

        from PyQt6.QtWidgets import QSpinBox, QPushButton
        spin_cantidad = QSpinBox()
        spin_cantidad.setRange(1, 9999)
        spin_cantidad.setValue(1)
        spin_cantidad.valueChanged.connect(self.recalcular_total)
        self.left_panel.table.setCellWidget(row_idx, 3, spin_cantidad)

        btn_delete = QPushButton("Eliminar")
        btn_delete.setObjectName("DeleteBtn")
        btn_delete.clicked.connect(lambda checked, r=row_idx: self.on_delete_item(r))
        self.left_panel.table.setCellWidget(row_idx, 4, btn_delete)

        self.recalcular_total()

    def on_delete_item(self, row_idx: int):
        self.left_panel.table.removeRow(row_idx)
        self.recalcular_total()

    def recalcular_total(self):
        total = 0.0
        row_count = self.left_panel.table.rowCount()
        for row in range(row_count):
            price_str = self.left_panel.table.item(row, 2).text()
            price_val = float(price_str.replace("$", ""))
            spin = self.left_panel.table.cellWidget(row, 3)
            quantity = spin.value() if spin else 1
            total += price_val * quantity
        self.right_panel.label_total_amount.setText(f"Total: ${total:.2f}")

    def find_table_row_by_barcode(self, barcode: str) -> int | None:
        for row in range(self.left_panel.table.rowCount()):
            item_barcode = self.left_panel.table.item(row, 0)
            if item_barcode and item_barcode.text() == barcode:
                return row
        return None

    def _increment_quantity_in_table(self, row_idx: int):
        spin = self.left_panel.table.cellWidget(row_idx, 3)
        if spin:
            spin.setValue(spin.value() + 1)
        self.recalcular_total()

    def _clear_table_and_total(self):
        self.left_panel.clear_table()
        self.right_panel.label_total_amount.setText("Total: $0.00")
        self.left_panel.search_input.clear()

    def on_cerrar_caja(self):
        """Abre la ventana de cierre de caja para ingresar el monto de cierre."""
        from .cierre_caja import CierreCajaWindow
        self.cierre_caja_window = CierreCajaWindow()
        self.cierre_caja_window.show()
