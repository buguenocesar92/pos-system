# src/components/loading_dialog.py

from PyQt6.QtWidgets import QDialog, QHBoxLayout, QLabel

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
