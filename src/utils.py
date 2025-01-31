# utils.py

import requests
from constants import (
    API_BASE_URL,
    ACCESS_TOKEN_FILE,
    REFRESH_TOKEN_FILE,
    HOST_FILE
)

############################################
# Lectura / Escritura de archivos
############################################
def read_file(file_path: str) -> str | None:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def write_file(file_path: str, content: str):
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    except IOError as e:
        raise IOError(f"Error al escribir en el archivo: {file_path}. Detalle: {str(e)}")

############################################
# SESIÓN GLOBAL PARA REUTILIZAR CONEXIÓN
############################################
SESSION = requests.Session()

############################################
# Lógica de refresh token
############################################
def attempt_refresh() -> bool:
    refresh_token = read_file(REFRESH_TOKEN_FILE)
    host = read_file(HOST_FILE)
    if not refresh_token or not host:
        return False

    headers = {
        "Authorization": f"Bearer {refresh_token}",
        "Accept": "application/json",
        "Host": host
    }

    url = f"{API_BASE_URL}/auth/refresh"
    try:
        r = SESSION.post(url, headers=headers)
        if r.status_code == 200:
            data = r.json()
            new_access = data.get("access_token")
            new_refresh = data.get("refresh_token")
            if new_access and new_refresh:
                write_file(ACCESS_TOKEN_FILE, new_access)
                write_file(REFRESH_TOKEN_FILE, new_refresh)
                return True
    except requests.RequestException:
        pass

    return False

def request_with_refresh(method: str, endpoint: str, data=None, json=None, headers=None, **kwargs) -> requests.Response:
    if headers is None:
        headers = {}

    access_token = read_file(ACCESS_TOKEN_FILE)
    host = read_file(HOST_FILE)

    if not access_token or not host:
        raise Exception("No hay token de acceso o host configurado.")

    headers["Authorization"] = f"Bearer {access_token}"
    headers["Host"] = host
    headers["Accept"] = "application/json"

    url = f"{API_BASE_URL}{endpoint}"

    response = SESSION.request(method, url, data=data, json=json, headers=headers, **kwargs)

    # Si 401 => intentar refresh
    if response.status_code == 401:
        if attempt_refresh():
            new_access_token = read_file(ACCESS_TOKEN_FILE)
            if new_access_token:
                headers["Authorization"] = f"Bearer {new_access_token}"
                response = SESSION.request(method, url, data=data, json=json, headers=headers, **kwargs)

    return response
