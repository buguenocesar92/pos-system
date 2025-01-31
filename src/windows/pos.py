# windows/pos.py

import requests
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QTableWidget, QTableWidgetItem, QAbstractItemView,
    QHeaderView, QComboBox, QSpinBox
)
from PyQt6.QtCore import Qt

from utils import request_with_refresh

class POSWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Venta de Productos")
        self.resize(900, 500)

        main_layout = QHBoxLayout(self)

        # ------ LADO IZQUIERDO (Búsqueda, Tabla, Paginación) ------
        left_layout = QVBoxLayout()

        # Barra de búsqueda
        search_layout = QHBoxLayout()

        lbl_search = QLabel("Código de Barras:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ingresa o escanea el código...")

        # (1) Permitir búsqueda con Enter:
        self.search_input.returnPressed.connect(self.on_search_barcode)

        # Botón de búsqueda
        self.btnBuscar = QPushButton("Buscar")
        self.btnBuscar.clicked.connect(self.on_search_barcode)

        search_layout.addWidget(lbl_search)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.btnBuscar)
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

        # ------ LADO DERECHO (Totales, Botones) ------
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

    # -------------------------------------------------
    # FUNCIÓN para BUSCAR un producto: /products/barcode/{barcode}
    # -------------------------------------------------
    def on_search_barcode(self):
        barcode = self.search_input.text().strip()
        if not barcode:
            QMessageBox.warning(self, "Atención", "Ingresa un código de barras.")
            return

        try:
            endpoint = f"/products/barcode/{barcode}"
            response = request_with_refresh("GET", endpoint)
            
            if response.status_code == 200:
                product = response.json()
                row_found = self.find_table_row_by_barcode(product.get("barcode", ""))
                if row_found is not None:
                    # Producto ya existe => aumentar la cantidad
                    spin = self.table.cellWidget(row_found, 3)
                    if spin:
                        spin.setValue(spin.value() + 1)
                    self.recalcular_total()
                else:
                    # Nuevo producto => agregar fila
                    self.add_product_to_table(product)

            elif response.status_code == 404:
                QMessageBox.information(self, "Sin resultados", "No se encontró producto con ese código.")
            elif response.status_code == 401:
                QMessageBox.critical(self, "Error", "Token expirado/no válido y no se pudo refrescar.")
            else:
                QMessageBox.critical(
                    self, "Error",
                    f"Error al buscar producto. Código HTTP: {response.status_code}"
                )

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

        # <--- Aquí limpiamos el input, ocurra lo que ocurra arriba.
        self.search_input.clear()


    # -------------------------------------------------
    # Busca si ya existe el barcode en la tabla
    # Retorna el índice de fila si lo encuentra, None si no
    # -------------------------------------------------
    def find_table_row_by_barcode(self, barcode):
        row_count = self.table.rowCount()
        for row in range(row_count):
            item_barcode = self.table.item(row, 0)  # Columna 0 => Código
            if item_barcode and item_barcode.text() == barcode:
                return row
        return None

    # -------------------------------------------------
    # Si no existe, insertamos una nueva fila con los datos
    # -------------------------------------------------
    def add_product_to_table(self, product):
        row_idx = self.table.rowCount()
        self.table.insertRow(row_idx)

        barcode = str(product.get("barcode", ""))
        name = str(product.get("name", ""))
        price_val = float(product.get("unit_price", 0.0))

        self.table.setItem(row_idx, 0, QTableWidgetItem(barcode))
        self.table.setItem(row_idx, 1, QTableWidgetItem(name))
        self.table.setItem(row_idx, 2, QTableWidgetItem(f"${price_val:.2f}"))

        # SpinBox de cantidad
        spin_cantidad = QSpinBox()
        spin_cantidad.setRange(1, 9999)
        spin_cantidad.setValue(1)
        # Al cambiar la cantidad => recalculamos
        spin_cantidad.valueChanged.connect(self.recalcular_total)
        self.table.setCellWidget(row_idx, 3, spin_cantidad)

        # Botón Eliminar
        btn_delete = QPushButton("🗑")
        btn_delete.clicked.connect(lambda _, r=row_idx: self.on_delete_item(r))
        self.table.setCellWidget(row_idx, 4, btn_delete)

        # Recalcular total
        self.recalcular_total()

    # -------------------------------------------------
    # Eliminar fila => removeRow
    # -------------------------------------------------
    def on_delete_item(self, row_idx):
        self.table.removeRow(row_idx)
        self.recalcular_total()

    # -------------------------------------------------
    # Recalcular total => iterar filas
    # -------------------------------------------------
    def recalcular_total(self):
        total = 0.0
        row_count = self.table.rowCount()

        for row in range(row_count):
            price_str = self.table.item(row, 2).text()  # ej: "$123.45"
            price_val = float(price_str.replace("$", ""))

            spin = self.table.cellWidget(row, 3)
            quantity = spin.value() if spin else 1

            total += price_val * quantity

        self.label_total_amount.setText(f"Total: ${total:.2f}")
