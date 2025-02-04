# src/components/left_panel.py

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QComboBox, QAbstractItemView, QHeaderView
)
from PyQt6.QtCore import Qt

class LeftPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # Barra de búsqueda
        search_layout = QHBoxLayout()
        lbl_search = QLabel("Código del Producto:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Escanea o ingresa código...")
        self.btnBuscar = QPushButton("Buscar")
        self.btnBuscar.setObjectName("BuscarBtn")  # Para CSS
        self.btnSync = QPushButton("Sync")
        self.btnSync.setObjectName("SyncBtn")
        search_layout.addWidget(lbl_search)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.btnBuscar)
        search_layout.addWidget(self.btnSync)
        layout.addLayout(search_layout)

        # Tabla de productos
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Código", "Descripción", "Precio", "Cantidad", "Acciones"])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

        # Paginación
        pagination_layout = QHBoxLayout()
        lbl_pagination = QLabel("Items per page:")
        self.combo_items_per_page = QComboBox()
        self.combo_items_per_page.addItems(["5", "10", "20", "50"])
        self.label_pagination_info = QLabel("1-1 of 1")
        self.btn_prev_page = QPushButton("◀")
        self.btn_prev_page.setObjectName("PrevPageBtn")
        self.btn_next_page = QPushButton("▶")
        self.btn_next_page.setObjectName("NextPageBtn")
        pagination_layout.addWidget(lbl_pagination)
        pagination_layout.addWidget(self.combo_items_per_page)
        pagination_layout.addWidget(self.label_pagination_info)
        pagination_layout.addWidget(self.btn_prev_page)
        pagination_layout.addWidget(self.btn_next_page)
        layout.addLayout(pagination_layout)

        self.setLayout(layout)

    def clear_table(self):
        self.table.clearContents()
        self.table.setRowCount(0)
