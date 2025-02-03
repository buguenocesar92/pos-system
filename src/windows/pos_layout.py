from PyQt6.QtWidgets import (
    QHBoxLayout, QVBoxLayout, QFrame, QLabel, QLineEdit,
    QPushButton, QComboBox, QTableWidget, QAbstractItemView,
    QHeaderView, QWidget
)
from PyQt6.QtCore import Qt

def build_left_container(parent) -> QFrame:
    """
    Crea el contenedor izquierdo con la barra de búsqueda, tabla y paginación.
    """
    container = QFrame()
    container.setObjectName("LeftContainer")
    layout = QVBoxLayout(container)

    # Barra de búsqueda
    search_layout = QHBoxLayout()
    lbl_search = QLabel("Código del Producto:")
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
    layout.addLayout(search_layout)

    # Tabla de productos
    parent.table = QTableWidget()
    parent.table.setColumnCount(5)
    parent.table.setHorizontalHeaderLabels(["Código", "Descripción", "Precio", "Cantidad", "Acciones"])
    parent.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    parent.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    parent.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    layout.addWidget(parent.table)

    # Paginación
    pagination_layout = QHBoxLayout()
    lbl_pagination = QLabel("Items per page:")
    parent.combo_items_per_page = QComboBox()
    parent.combo_items_per_page.addItems(["5", "10", "20", "50"])
    parent.label_pagination_info = QLabel("1-1 of 1")
    parent.btn_prev_page = QPushButton("◀")
    parent.btn_next_page = QPushButton("▶")
    pagination_layout.addWidget(lbl_pagination)
    pagination_layout.addWidget(parent.combo_items_per_page)
    pagination_layout.addWidget(parent.label_pagination_info)
    pagination_layout.addWidget(parent.btn_prev_page)
    pagination_layout.addWidget(parent.btn_next_page)
    layout.addLayout(pagination_layout)

    return container

def build_right_container(parent) -> QFrame:
    """
    Crea el contenedor derecho con los totales y los botones.
    """
    container = QFrame()
    container.setObjectName("RightContainer")
    layout = QVBoxLayout(container)

    # Título de totales
    lbl_totales = QLabel("Totales")
    lbl_totales.setObjectName("TitleTotals")
    layout.addWidget(lbl_totales, alignment=Qt.AlignmentFlag.AlignLeft)

    # Total
    parent.label_total_amount = QLabel("Total: $0.00")
    parent.label_total_amount.setObjectName("TotalAmount")
    layout.addWidget(parent.label_total_amount, alignment=Qt.AlignmentFlag.AlignLeft)

    layout.addSpacing(20)

    # Botones
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
