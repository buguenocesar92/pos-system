# windows/pos.py

import requests
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QTableWidget, QTableWidgetItem, QAbstractItemView,
    QHeaderView, QComboBox, QSpinBox
)
from PyQt6.QtCore import Qt

# Importa tu función de peticiones seguras (refresh)
from utils import request_with_refresh


class POSWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Venta de Productos")
        self.resize(900, 500)

        # Layout principal: contenedor horizontal
        main_layout = QHBoxLayout(self)

        # ------------------ LADO IZQUIERDO ------------------
        # Contiene: barra de búsqueda, tabla, paginación
        left_layout = QVBoxLayout()

        # 1) Barra de búsqueda
        search_layout = QHBoxLayout()
        lbl_search = QLabel("Código del Producto:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar producto...")

        # Botón que usaremos para actualizar o buscar
        self.btnActualizar = QPushButton("Actualizar Productos")
        self.btnActualizar.clicked.connect(self.obtener_productos)

        search_layout.addWidget(lbl_search)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.btnActualizar)
        left_layout.addLayout(search_layout)

        # 2) Tabla de productos
        self.table = QTableWidget()
        # Definir columnas que se parezcan a las de tu diseño
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Código de Barras", "Descripción", "Precio", "Cantidad", "Acciones"])
        # Ajustar el modo de edición
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # Ajustar las columnas para que ocupen todo el ancho
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # Seleccionar toda la fila al hacer clic
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        left_layout.addWidget(self.table)

        # 3) Controles de paginación (opcional)
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

        # ------------------ LADO DERECHO ------------------
        # Contiene: Totales + botones (Confirmar, Cancelar, Cerrar Caja)
        right_layout = QVBoxLayout()

        # Título totales
        label_totales = QLabel("Totales")
        label_totales.setStyleSheet("font-weight: bold; font-size: 16px;")
        right_layout.addWidget(label_totales, alignment=Qt.AlignmentFlag.AlignLeft)

        # Label para mostrar total
        self.label_total_amount = QLabel("Total: $0.00")
        self.label_total_amount.setStyleSheet("font-size: 14px;")
        right_layout.addWidget(self.label_total_amount, alignment=Qt.AlignmentFlag.AlignLeft)

        right_layout.addSpacing(20)

        # Botones de acción
        self.btn_confirmar_venta = QPushButton("CONFIRMAR VENTA")
        self.btn_cancelar_venta = QPushButton("CANCELAR VENTA")
        self.btn_cerrar_caja = QPushButton("CERRAR CAJA")

        # Si quieres conectar funciones:
        # self.btn_confirmar_venta.clicked.connect(self.on_confirmar_venta)
        # self.btn_cancelar_venta.clicked.connect(self.on_cancelar_venta)
        # self.btn_cerrar_caja.clicked.connect(self.on_cerrar_caja)

        right_layout.addWidget(self.btn_confirmar_venta)
        right_layout.addWidget(self.btn_cancelar_venta)
        right_layout.addWidget(self.btn_cerrar_caja)
        right_layout.addStretch()

        main_layout.addLayout(right_layout, stretch=1)

        # (Opcional) Llenar tabla con algún ejemplo inicial
        self.populate_initial_example()

    def populate_initial_example(self):
        """Datos de prueba (puedes omitirlo o cargar datos en obtener_productos)."""
        self.table.setRowCount(1)
        self.table.setItem(0, 0, QTableWidgetItem("074312038228"))  # Código
        self.table.setItem(0, 1, QTableWidgetItem("Omega 3"))       # Descripción
        self.table.setItem(0, 2, QTableWidgetItem("$138.00"))       # Precio

        # SpinBox para la cantidad
        spin_cantidad = QSpinBox()
        spin_cantidad.setRange(1, 9999)
        spin_cantidad.setValue(1)
        self.table.setCellWidget(0, 3, spin_cantidad)

        # Botón de eliminar (o acción)
        btn_delete = QPushButton("🗑")
        # btn_delete.clicked.connect(lambda: self.on_delete_item(0))
        self.table.setCellWidget(0, 4, btn_delete)

        # Actualizar total
        self.label_total_amount.setText("Total: $138.00")

    def obtener_productos(self):
        """
        Llama a la API /products usando el token (con soporte de refresh).
        Carga los productos en la tabla.
        """
        try:
            response = request_with_refresh("GET", "/products")
            if response.status_code == 200:
                productos = response.json().get("items", [])
                self.cargar_en_tabla(productos)
            elif response.status_code == 401:
                # Significa que ni refrescando se pudo
                QMessageBox.critical(
                    self, "Error",
                    "Tu token ha expirado y no se pudo refrescar. Por favor, inicia sesión de nuevo."
                )
            else:
                QMessageBox.critical(
                    self, "Error",
                    f"Error al obtener productos: {response.status_code}"
                )
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def cargar_en_tabla(self, productos):
        """
        Llena la tabla con la lista de productos que devuelva tu API.
        Cada producto se asume que tiene: { 'barcode', 'name', 'unit_price' }
        Ajusta según la estructura real de tu respuesta.
        """
        self.table.clearContents()
        self.table.setRowCount(len(productos))

        total = 0.0

        for row_idx, prod in enumerate(productos):
            barcode = str(prod.get("barcode", ""))
            name = str(prod.get("name", ""))
            price_val = prod.get("unit_price", 0.0)

            self.table.setItem(row_idx, 0, QTableWidgetItem(barcode))
            self.table.setItem(row_idx, 1, QTableWidgetItem(name))
            self.table.setItem(row_idx, 2, QTableWidgetItem(f"${price_val:.2f}"))

            # SpinBox para cantidad (por defecto 1)
            spin_cantidad = QSpinBox()
            spin_cantidad.setRange(1, 9999)
            spin_cantidad.setValue(1)
            # Podrías conectar un método para recalcular total al cambiar
            # spin_cantidad.valueChanged.connect(lambda val, row=row_idx, unit=price_val: self.recalcular_total(val, unit, row))
            self.table.setCellWidget(row_idx, 3, spin_cantidad)

            # Botón eliminar
            btn_delete = QPushButton("🗑")
            # btn_delete.clicked.connect(lambda checked, r=row_idx: self.on_delete_item(r))
            self.table.setCellWidget(row_idx, 4, btn_delete)

            # Sumar al total (price_val * 1)
            total += price_val

        self.label_total_amount.setText(f"Total: ${total:.2f}")

    # Ejemplos opcionales de funciones de apoyo:
    # def on_delete_item(self, row_idx):
    #     self.table.removeRow(row_idx)
    #     # Ajustar total en consecuencia...

    # def recalcular_total(self, cantidad, unit_price, row):
    #     # Recalcular total general en base a todos los rows, etc.
    #     pass

    # def on_confirmar_venta(self):
    #     # Lógica para enviar la venta
    #     pass

    # def on_cancelar_venta(self):
    #     # Lógica para cancelar
    #     pass

    # def on_cerrar_caja(self):
    #     # Lógica para cerrar caja
    #     pass
