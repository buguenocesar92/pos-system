# src/components/right_panel.py

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt

class RightPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # Totales
        lbl_totales = QLabel("Totales")
        layout.addWidget(lbl_totales, alignment=Qt.AlignmentFlag.AlignLeft)
        self.label_total_amount = QLabel("Total: $0.00")
        layout.addWidget(self.label_total_amount, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addSpacing(20)

        # Botones
        self.btn_confirmar_venta = QPushButton("CONFIRMAR VENTA")
        self.btn_confirmar_venta.setObjectName("ConfirmBtn")
        self.btn_cancelar_venta = QPushButton("CANCELAR VENTA")
        self.btn_cancelar_venta.setObjectName("CancelBtn")
        self.btn_cerrar_caja = QPushButton("CERRAR CAJA")
        self.btn_cerrar_caja.setObjectName("CloseBtn")
        layout.addWidget(self.btn_confirmar_venta)
        layout.addWidget(self.btn_cancelar_venta)
        layout.addWidget(self.btn_cerrar_caja)
        layout.addStretch()

        self.setLayout(layout)
