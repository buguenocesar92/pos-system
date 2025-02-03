# sync_worker.py
from PyQt6.QtCore import QThread, pyqtSignal
from sync import sync_all_products  # Asegúrate de que sync_all_products esté correctamente definido

class SyncWorker(QThread):
    finished = pyqtSignal(object)  # Emitirá un mensaje de éxito o la excepción ocurrida

    def run(self):
        try:
            sync_all_products()  # Ejecuta la sincronización
            self.finished.emit("Sincronización completada.")
        except Exception as e:
            self.finished.emit(e)
