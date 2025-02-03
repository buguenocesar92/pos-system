# windows/pos_layout.py

from PyQt6.QtWidgets import (
    QHBoxLayout, QVBoxLayout, QFrame, QLabel, QLineEdit,
    QPushButton, QComboBox, QTableWidget, QAbstractItemView,
    QHeaderView, QSpinBox, QWidget
)
from PyQt6.QtCore import Qt

def build_left_container(parent) -> QFrame:
    """
    Crea el contenedor izquierdo (búsqueda, tabla, paginación).
    'parent' es la instancia de POSWindow (o quien la use),
    donde se asignan propiedades como parent.table, parent.search_input...
    """
    container = QFrame()
    container.setObjectName("LeftContainer")
    layout = QVBoxLayout(container)

    # Barra de búsqueda
    search_layout = _build_search_bar(parent)
    layout.addLayout(search_layout)

    # Tabla de productos
    parent.table = _build_products_table()
    layout.addWidget(parent.table)

    # Sección de paginación
    pagination_layout = _build_pagination_area(parent)
    layout.addLayout(pagination_layout)

    return container

def _build_search_bar(parent) -> QHBoxLayout:
    search_layout = QHBoxLayout()

    lbl_search = QLabel("Código de Barras:")
    parent.search_input = QLineEdit()
    parent.search_input.setPlaceholderText("Ingresa o escanea el código...")

    parent.btnBuscar = QPushButton("Buscar")
    parent.btnBuscar.setObjectName("BuscarBtn")

    parent.btnSync = QPushButton("Sync")
    parent.btnSync.setObjectName("SyncBtn")

    search_layout.addWidget(lbl_search)
    search_layout.addWidget(parent.search_input)
    search_layout.addWidget(parent.btnBuscar)
    search_layout.addWidget(parent.btnSync)

    return search_layout

def _build_products_table() -> QTableWidget:
    table = QTableWidget()
    table.setColumnCount(5)
    table.setHorizontalHeaderLabels(["Código", "Descripción", "Precio", "Cantidad", "Acciones"])
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    return table

def _build_pagination_area(parent) -> QHBoxLayout:
    pagination_layout = QHBoxLayout()

    pagination_layout.addWidget(QLabel("Items per page:"))

    parent.combo_items_per_page = QComboBox()
    parent.combo_items_per_page.addItems(["5", "10", "20", "50"])
    parent.combo_items_per_page.setCurrentText("10")
    pagination_layout.addWidget(parent.combo_items_per_page)

    parent.label_pagination_info = QLabel("1-1 of 1")
    pagination_layout.addWidget(parent.label_pagination_info)

    parent.btn_prev_page = QPushButton("◀")
    parent.btn_next_page = QPushButton("▶")

    pagination_layout.addWidget(parent.btn_prev_page)
    pagination_layout.addWidget(parent.btn_next_page)
    pagination_layout.addStretch()

    return pagination_layout

def build_right_container(parent) -> QFrame:
    """
    Crea el contenedor derecho (Totales y botones).
    """
    container = QFrame()
    container.setObjectName("RightContainer")
    layout = QVBoxLayout(container)

    lbl_totales = QLabel("Totales")
    lbl_totales.setObjectName("TitleTotals")
    layout.addWidget(lbl_totales, alignment=Qt.AlignmentFlag.AlignLeft)

    parent.label_total_amount = QLabel("Total: $0.00")
    parent.label_total_amount.setObjectName("TotalAmount")
    layout.addWidget(parent.label_total_amount, alignment=Qt.AlignmentFlag.AlignLeft)

    layout.addSpacing(20)

    parent.btn_confirmar_venta = QPushButton("CONFIRMAR VENTA")
    parent.btn_confirmar_venta.setObjectName("ConfirmBtn")

    parent.btn_cancelar_venta = QPushButton("CANCELAR VENTA")
    parent.btn_cancelar_venta.setObjectName("CancelBtn")

    parent.btn_cerrar_caja = QPushButton("CERRAR CAJA")
    parent.btn_cerrar_caja.setObjectName("CloseBtn")

    layout.addWidget(parent.btn_confirmar_venta)
    layout.addWidget(parent.btn_cancelar_venta)
    layout.addWidget(parent.btn_cerrar_caja)
    layout.addStretch()

    return container
