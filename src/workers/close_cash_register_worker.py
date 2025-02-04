# src/close_cash_register_worker.py

from PyQt6.QtCore import QThread, pyqtSignal
import requests
from src.constants import API_BASE_URL, ACCESS_TOKEN_FILE, HOST_FILE
from src.utils import read_file

class CloseCashRegisterWorker(QThread):
    """
    Worker que realiza la petición POST para cerrar la caja mediante el endpoint /cash-register/close.
    Emite la señal 'finished' con la respuesta (un diccionario) en caso de éxito, o con una excepción en caso de error.
    """
    finished = pyqtSignal(object)
    
    def __init__(self, closing_amount):
        """
        :param closing_amount: Monto de cierre (por ejemplo, 1200.0)
        """
        super().__init__()
        self.closing_amount = closing_amount

    def run(self):
        try:
            # Leer el host configurado
            host = read_file(HOST_FILE)
            if not host:
                raise Exception("El Host no está configurado.")
            
            # Leer el token de acceso
            token = read_file(ACCESS_TOKEN_FILE)
            if not token:
                raise Exception("El token de acceso no está disponible.")
            
            url = f"{API_BASE_URL}/cash-register/close"
            data = {"closing_amount": self.closing_amount}
            headers = {
                "Accept": "application/json",
                "Host": host,
                "Authorization": f"Bearer {token}"
            }
            
            response = requests.post(url, headers=headers, data=data)
            if response.status_code in (200, 201):
                self.finished.emit(response.json())
            else:
                raise Exception(f"Error al cerrar caja. Código: {response.status_code} - {response.text}")
        except Exception as e:
            self.finished.emit(e)
