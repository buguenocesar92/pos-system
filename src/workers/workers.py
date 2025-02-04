from PyQt6.QtCore import QThread, pyqtSignal
from src.utils import request_with_refresh

class WorkerThread(QThread):
    """
    Hilo para procesar la venta sin bloquear la UI.
    """
    finished = pyqtSignal(object)  # Señal para enviar la respuesta al hilo principal

    def __init__(self, payload):
        super().__init__()
        self.payload = payload

    def run(self):
        """Ejecuta la petición en un hilo secundario."""
        try:
            response = request_with_refresh("POST", "/sales", json=self.payload)
            self.finished.emit(response)  # Enviamos la respuesta
        except Exception as e:
            self.finished.emit(e)  # Enviamos el error
