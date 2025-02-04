# src/cierre_caja.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QApplication
from PyQt6.QtGui import QFont, QGuiApplication
from PyQt6.QtCore import Qt
from src.workers.close_cash_register_worker import CloseCashRegisterWorker
from src.loading_dialog import MaterialLoadingDialog

class CierreCajaWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cierre de Caja")
        self.setFixedSize(400, 300)
        self.setup_ui()
        self.center_window()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # Título o instrucción
        titulo = QLabel("Ingrese el monto de cierre de caja")
        titulo.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(titulo)

        # Campo para ingresar el monto de cierre
        self.closing_amount_input = QLineEdit()
        self.closing_amount_input.setPlaceholderText("Monto de cierre")
        self.closing_amount_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d9d9d9;
                border-radius: 5px;
                background: #F5F5F5;
                padding: 10px;
                font-size: 14px;
                color: #333333;
            }
            QLineEdit:focus {
                border: 1px solid #4A90E2;
                background: #FFFFFF;
            }
        """)
        layout.addWidget(self.closing_amount_input)

        # Botón de confirmación
        self.confirm_button = QPushButton("Confirmar Cierre")
        self.confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
            QPushButton:pressed {
                background-color: #2C5A94;
            }
        """)
        self.confirm_button.clicked.connect(self.confirm)
        layout.addWidget(self.confirm_button)

        self.setLayout(layout)

    def center_window(self):
        """ Centra la ventana en la pantalla. """
        screen_geometry = QGuiApplication.primaryScreen().geometry()
        center_x = (screen_geometry.width() - self.width()) // 2
        center_y = (screen_geometry.height() - self.height()) // 2
        self.move(center_x, center_y)

    def confirm(self):
        closing_amount_text = self.closing_amount_input.text().strip()
        try:
            closing_amount = float(closing_amount_text)
        except ValueError:
            QMessageBox.critical(self, "Error", "El monto de cierre debe ser un número válido.")
            return

        # Mostrar un diálogo de carga mientras se cierra la caja
        self.loading_dialog = MaterialLoadingDialog(self, "Cerrando caja, por favor espere...")
        self.loading_dialog.show()

        # Iniciar el worker para cerrar caja
        self.close_worker = CloseCashRegisterWorker(closing_amount)
        self.close_worker.finished.connect(self.handle_close_finished)
        self.close_worker.start()

    def handle_close_finished(self, result):
        self.loading_dialog.close()
        if isinstance(result, Exception):
            QMessageBox.critical(self, "Error al cerrar caja", str(result))
        else:
            QMessageBox.information(self, "Éxito", "Caja cerrada exitosamente.")
            # Cerrar la aplicación o todas las ventanas
            QApplication.quit()
