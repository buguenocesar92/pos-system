# windows/pos.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QTableWidget, QTableWidgetItem,
    QAbstractItemView, QHeaderView, QComboBox, QSpinBox
)
from PyQt6.QtCore import Qt

from local_db import get_product_by_barcode
from sync import sync_all_products  # para refrescar manualmente, si quieres
from local_db import init_db

class POSWindow(QWidget):
    def __init__(self):
        super().__init__()
        init_db()  # Asegurarnos de tener la tabla
        self.setWindowTitle("Venta de Productos")
        self.resize(900, 500)

        main_layout = QHBoxLayout(self)

        left_layout = QVBoxLayout()
        # Barra de búsqueda
        search_layout = QHBoxLayout()
        lbl_search = QLabel("Código de Barras:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ingresa o escanea el código...")

        # ENTER => buscar
        self.search_input.returnPressed.connect(self.on_search_barcode)

        # Botón Buscar
        self.btnBuscar = QPushButton("Buscar")
        self.btnBuscar.clicked.connect(self.on_search_barcode)

        # Botón opcional de "Sync" para actualizar la base local
        self.btnSync = QPushButton("Sync")
        self.btnSync.clicked.connect(self.on_sync_products)

        search_layout.addWidget(lbl_search)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.btnBuscar)
        search_layout.addWidget(self.btnSync)
        left_layout.addLayout(search_layout)

        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Código", "Descripción", "Precio", "Cantidad", "Acciones"])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        left_layout.addWidget(self.table)

        # Paginación (opcional)
        pagination_layout = QHBoxLayout()
        self.combo_items_per_page = QComboBox()
        self.combo_items_per_page.addItems(["5", "10", "20", "50"])
        self.combo_items_per_page.setCurrentText("10")
        self.label_pagination_info = QLabel("1-1 of 1")
        self.btn_prev_page = QPushButton("◀")
        self.btn_next_page = QPushButton("▶")

        pagination_layout.addWidget(QLabel("Items per page:"))
        pagination_layout.addWidget(self.combo_items_per_page)
        pagination_layout.addWidget(self.label_pagination_info)
        pagination_layout.addWidget(self.btn_prev_page)
        pagination_layout.addWidget(self.btn_next_page)
        pagination_layout.addStretch()
        left_layout.addLayout(pagination_layout)

        main_layout.addLayout(left_layout, stretch=3)

        # Lado derecho (totales + botones)
        right_layout = QVBoxLayout()
        lbl_totales = QLabel("Totales")
        lbl_totales.setStyleSheet("font-weight: bold; font-size: 16px;")
        right_layout.addWidget(lbl_totales, alignment=Qt.AlignmentFlag.AlignLeft)

        self.label_total_amount = QLabel("Total: $0.00")
        self.label_total_amount.setStyleSheet("font-size: 14px;")
        right_layout.addWidget(self.label_total_amount, alignment=Qt.AlignmentFlag.AlignLeft)

        right_layout.addSpacing(20)

        self.btn_confirmar_venta = QPushButton("CONFIRMAR VENTA")
        self.btn_cancelar_venta = QPushButton("CANCELAR VENTA")
        self.btn_cerrar_caja = QPushButton("CERRAR CAJA")

        right_layout.addWidget(self.btn_confirmar_venta)
        right_layout.addWidget(self.btn_cancelar_venta)
        right_layout.addWidget(self.btn_cerrar_caja)
        right_layout.addStretch()

        main_layout.addLayout(right_layout, stretch=1)
        self.setLayout(main_layout)

    def on_search_barcode(self):
        barcode = self.search_input.text().strip()
        if not barcode:
            QMessageBox.warning(self, "Atención", "Ingresa un código de barras.")
            return

        product = get_product_by_barcode(barcode)
        if product:
            row_found = self.find_table_row_by_barcode(product["barcode"])
            if row_found is not None:
                # ya existe => aumentar cantidad
                spin = self.table.cellWidget(row_found, 3)
                if spin:
                    spin.setValue(spin.value() + 1)
                self.recalcular_total()
            else:
                # Agregar nueva fila
                self.add_product_to_table(product)
        else:
            QMessageBox.information(self, "Sin resultados", f"No se encontró producto '{barcode}' en la base local.")

        # Limpiar input
        self.search_input.clear()

    def on_sync_products(self):
        """
        Llama a sync_all_products() para refrescar la base local.
        """
        sync_all_products()
        QMessageBox.information(self, "Sync", "Productos sincronizados.")

    def add_product_to_table(self, product):
        row_idx = self.table.rowCount()
        self.table.insertRow(row_idx)

        barcode = product.get("barcode", "")
        name = product.get("name", "")
        price_val = product.get("unit_price", 0.0)

        self.table.setItem(row_idx, 0, QTableWidgetItem(str(barcode)))
        self.table.setItem(row_idx, 1, QTableWidgetItem(str(name)))
        self.table.setItem(row_idx, 2, QTableWidgetItem(f"${price_val:.2f}"))

        spin_cantidad = QSpinBox()
        spin_cantidad.setRange(1, 9999)
        spin_cantidad.setValue(1)
        spin_cantidad.valueChanged.connect(self.recalcular_total)
        self.table.setCellWidget(row_idx, 3, spin_cantidad)

        btn_delete = QPushButton("🗑")
        btn_delete.clicked.connect(lambda _, r=row_idx: self.on_delete_item(r))
        self.table.setCellWidget(row_idx, 4, btn_delete)

        self.recalcular_total()

    def on_delete_item(self, row_idx):
        self.table.removeRow(row_idx)
        self.recalcular_total()

    def recalcular_total(self):
        total = 0.0
        rows = self.table.rowCount()
        for row in range(rows):
            price_str = self.table.item(row, 2).text()  # "$123.45"
            price_val = float(price_str.replace("$", ""))

            spin = self.table.cellWidget(row, 3)
            quantity = spin.value() if spin else 1

            total += price_val * quantity
        self.label_total_amount.setText(f"Total: ${total:.2f}")

    def find_table_row_by_barcode(self, barcode):
        """
        Retorna el número de fila si encuentra 'barcode' en la columna 0, o None si no.
        """
        for row in range(self.table.rowCount()):
            item_barcode = self.table.item(row, 0)
            if item_barcode and item_barcode.text() == barcode:
                return row
        return None
