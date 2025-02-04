from PyQt6.QtCore import QThread, pyqtSignal
from src.sync import sync_all_products


class SyncWorker(QThread):
    """Hilo para sincronizar productos con la nube."""
    finished = pyqtSignal(object)

    def run(self):
        """Ejecuta la sincronización en un hilo secundario."""
        try:
            result = sync_all_products()
            self.finished.emit(result)  # Emite el resultado si todo va bien
        except Exception as e:
            self.finished.emit(e)  # Emite el error en caso de fallo
