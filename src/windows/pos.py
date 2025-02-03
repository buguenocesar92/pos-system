import os
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QDialog, QLabel, QMessageBox, QTableWidgetItem, QSpinBox, QPushButton
)
from PyQt6.QtCore import Qt

from local_db import init_db, get_product_by_barcode
from windows.pos_layout import build_left_container, build_right_container
from windows.pos_controller import connect_signals
from sync import sync_all_products
from sync_worker import SyncWorker  # Asegúrate de importar la clase SyncWorker
from workers import WorkerThread    # Importamos el WorkerThread extraído


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

    SYNC_INTERVAL_MS = 1 * 60 * 1000  # 5 minutos

    def __init__(self):
        super().__init__()
        init_db()  # Crea/actualiza la base local

        self.setWindowTitle("Venta de Productos")
        self.resize(900, 500)

        # 1) Construir la interfaz
        self._init_main_layout()

        # 2) Cargar estilos
        self._load_stylesheet()

        # 3) Conectar eventos
        connect_signals(self)

    def _init_main_layout(self):
        main_layout = QHBoxLayout(self)

        self.left_container = build_left_container(self)
        self.right_container = build_right_container(self)

        main_layout.addWidget(self.left_container, stretch=3)
        main_layout.addWidget(self.right_container, stretch=1)

        self.setLayout(main_layout)

    def _load_stylesheet(self):
        style_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "styles",
            "pos_style.qss"
        )
        try:
            with open(style_path, "r", encoding="utf-8") as f:
                style_sheet = f.read()
            self.setStyleSheet(style_sheet)
        except FileNotFoundError:
            print(f"[WARNING] No se encontró el archivo de estilos: {style_path}")

    # ----------------------------------------------------------------
    # Métodos de Lógica / Eventos
    # ----------------------------------------------------------------
    def on_search_barcode(self):
        """
        Maneja la búsqueda de un producto por código de barras.
        """
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
        """
        Sincroniza manualmente los productos con la nube en un hilo separado sin bloquear la UI.
        """
        self.sync_worker = SyncWorker()
        self.sync_worker.finished.connect(self.handle_sync_finished)
        self.sync_worker.start()

    def handle_sync_finished(self, result):
        """
        Maneja el resultado del hilo de sincronización sin mostrar un diálogo.
        """
        if isinstance(result, Exception):
            print(f"Error en sincronización: {result}")
        else:
            print(result)

    def on_confirmar_venta(self):
        """
        Registra la venta usando hilos (QThread) para evitar congelar la UI.
        """
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
        """
        Maneja la respuesta del hilo secundario.
        """
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
        """
        Sincroniza la base de datos local con la nube.
        """
        sync_all_products()
        print("Auto-sync completado.")

    # ----------------------------------------------------------------
    # Método para Cancelar la Venta
    # ----------------------------------------------------------------
    def on_cancelar_venta(self):
        """
        Cancela la venta borrando todos los productos de la tabla.
        Solicita confirmación antes de cancelar.
        """
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
        """
        Agrega un producto a la tabla.
        """
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
        """
        Elimina un producto de la tabla.
        """
        self.table.removeRow(row_idx)
        self.recalcular_total()

    def recalcular_total(self):
        """
        Recalcula el total de la venta.
        """
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
        """
        Encuentra un producto en la tabla por código de barras.
        """
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
        """
        Borra el contenido de la tabla, resetea el total y limpia el campo de búsqueda.
        """
        self.table.clearContents()
        self.table.setRowCount(0)
        self.label_total_amount.setText("Total: $0.00")
        self.search_input.clear()
