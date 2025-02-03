# sync_worker.py
from PyQt6.QtCore import QThread, pyqtSignal
from sync import sync_all_products

class SyncWorker(QThread):
    # Señal que enviará un mensaje o excepción al terminar
    finished = pyqtSignal(object)

    def run(self):
        try:
            sync_all_products()  # Ejecuta la sincronización
            self.finished.emit("Sincronización completada.")  # Emite un mensaje de éxito
        except Exception as e:
            self.finished.emit(e)  # Emite el error en caso de excepción
