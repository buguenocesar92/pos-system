from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QApplication
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QPainter, QPen, QColor
import sys


class MaterialLoadingDialog(QDialog):
    def __init__(self, parent=None, message="Cargando..."):
        super().__init__(parent)

        # Configurar la ventana sin bordes y con fondo oscuro
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setModal(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Estilo general
        self.setStyleSheet("""
        QDialog {
            background-color: rgba(0, 0, 0, 180);  /* Fondo semi-transparente */
            border-radius: 10px;
        }
        QLabel {
            color: white;  /* Texto blanco */
            font-size: 16px;  /* Tamaño del texto */
            font-weight: bold;  /* Texto en negrita */
        }
        """)

        # Configurar el layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Etiqueta del mensaje
        self.label = QLabel(message, self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Añadir la etiqueta al layout
        layout.addWidget(self.label)
        self.setLayout(layout)

        # Configurar el tamaño del diálogo
        self.setFixedSize(200, 200)

        # Configurar el spinner
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_spinner)
        self.timer.start(50)  # Actualizar cada 50ms

    def update_spinner(self):
        """Actualiza el ángulo del spinner."""
        self.angle = (self.angle + 10) % 360  # Incrementar el ángulo
        self.update()

    def paintEvent(self, event):
        """Dibuja el spinner en el centro del diálogo."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Configurar el área de dibujo
        size = self.width()
        rect = QRectF(size / 4, size / 4, size / 2, size / 2)  # Spinner centrado
        
