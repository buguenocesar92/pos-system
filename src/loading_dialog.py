from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QMovie
import os

class MaterialLoadingDialog(QDialog):
    def __init__(self, parent=None, message="Cargando..."):
        super().__init__(parent)
        # Eliminar marco y fondo para un diseño moderno
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setModal(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Configurar el layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Etiqueta del mensaje
        self.label = QLabel(message)
        self.label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Etiqueta del GIF de carga
        self.loading_label = QLabel(self)
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Ruta absoluta del GIF
        gif_path = os.path.join(os.path.dirname(__file__), "assets", "loading.gif")

        if os.path.exists(gif_path):  # Verifica si el archivo existe
            self.movie = QMovie(gif_path)
            self.movie.setScaledSize(QSize(100, 100))  # 🔹 Ajusta el tamaño del GIF (px)
            self.loading_label.setMovie(self.movie)
            self.movie.start()  # Inicia la animación
        else:
            self.loading_label.setText("⚠️ GIF no encontrado")  # Mensaje si no se encuentra

        layout.addWidget(self.loading_label)
        layout.addWidget(self.label)
        self.setLayout(layout)
