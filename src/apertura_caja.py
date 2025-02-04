# windows/apertura_caja.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtGui import QFont, QGuiApplication
from PyQt6.QtCore import Qt
from src.workers.open_cash_register_worker import OpenCashRegisterWorker

# Si utilizas un diálogo de carga, asegúrate de importarlo.
from src.loading_dialog import MaterialLoadingDialog  # O el nombre que utilices

class AperturaCajaWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Apertura de Caja")
        self.setFixedSize(400, 300)
        self.setup_ui()
        self.center_window()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # Título
        titulo = QLabel("Ingrese el monto de apertura de caja")
        titulo.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(titulo)

        # Campo para ingresar el monto
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Monto de apertura")
        self.amount_input.setStyleSheet("""
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
        layout.addWidget(self.amount_input)

        # Botón de confirmación
        self.confirm_button = QPushButton("Confirmar")
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
        monto_texto = self.amount_input.text().strip()
        try:
            monto = float(monto_texto)
            if monto < 0:
                raise ValueError("El monto no puede ser negativo.")
        except ValueError:
            QMessageBox.critical(self, "Error", "Ingrese un monto válido.")
            return
        
        print("Valor enviado para apertura:", monto)  # Para debug

        self.loading_dialog = MaterialLoadingDialog(self, "Abriendo caja, por favor espere...")
        self.loading_dialog.show()

        self.worker = OpenCashRegisterWorker(monto)
        self.worker.finished.connect(self.handle_open_finished)
        self.worker.start()


    def handle_open_finished(self, result):
        """ Maneja la respuesta de la petición POST al endpoint de apertura de caja. """
        self.loading_dialog.close()
        if isinstance(result, Exception):
            QMessageBox.critical(self, "Error", f"Error al abrir la caja: {result}")
        else:
            # Se asume que la respuesta contiene un mensaje de éxito.
            message = result.get("message", "Caja abierta correctamente.")
            QMessageBox.information(self, "Éxito", message)

            # Luego de abrir la caja, se abre la ventana del POS.
            from src.pos import POSWindow
            self.pos_window = POSWindow()
            self.pos_window.show()
            self.close()
