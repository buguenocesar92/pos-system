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
    """
    Lee el contenido de un archivo y lo retorna como string.
    Si no existe, retorna None.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


def write_file(file_path: str, content: str):
    """
    Escribe 'content' en el archivo file_path.
    Si hay error de escritura, lanza IOError.
    """
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
    """
    Llama a /auth/refresh con el refresh_token.
    Si todo va bien, reemplaza los archivos de access_token y refresh_token
    con los nuevos valores, y retorna True.
    Caso contrario, retorna False.
    """
    refresh_token = read_file(REFRESH_TOKEN_FILE)
    host = read_file(HOST_FILE)

    if not refresh_token or not host:
        # Si no tenemos refresh_token o host configurado, no podemos refrescar.
        return False

    # Cabeceras para pedir refresh
    headers = {
        "Authorization": f"Bearer {refresh_token}",  # <-- Usamos el refresh_token
        "Accept": "application/json",
        "Host": host
    }

    url = f"{API_BASE_URL}/auth/refresh"
    try:
        # 1) USAMOS SESSION.post EN LUGAR DE requests.post
        r = SESSION.post(url, headers=headers)

        if r.status_code == 200:
            data = r.json()
            # El backend retorna algo como:
            # {
            #   "access_token": "...",
            #   "refresh_token": "...",
            #   "token_type": "bearer",
            #   "expires_in": ...
            # }
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
    """
    Realiza una petición a la API usando el access_token.
    Si recibe 401, intenta refrescar con el refresh_token y reintenta.

    :param method: e.g. "GET", "POST", etc.
    :param endpoint: e.g. "/products", "/auth/me"
    :param data: si envías form-data
    :param json: si envías JSON
    :param headers: dict de cabeceras
    :param kwargs: cualquier otro argumento (params, timeout, etc.)
    :return: objeto requests.Response
    """
    if headers is None:
        headers = {}

    # Cargamos el access_token actual
    access_token = read_file(ACCESS_TOKEN_FILE)
    host = read_file(HOST_FILE)

    if not access_token or not host:
        raise Exception("No hay token de acceso o host configurado.")

    headers["Authorization"] = f"Bearer {access_token}"
    headers["Host"] = host
    headers["Accept"] = "application/json"

    url = f"{API_BASE_URL}{endpoint}"

    # 1) Hacemos la petición original usando la SESIÓN
    response = SESSION.request(
        method=method,
        url=url,
        data=data,
        json=json,
        headers=headers,
        **kwargs
    )

    # 2) Si regresa 401, intentamos refrescar y reintentar
    if response.status_code == 401:
        if attempt_refresh():
            # Si refrescó correctamente, leemos el nuevo access_token
            new_access_token = read_file(ACCESS_TOKEN_FILE)
            if new_access_token:
                headers["Authorization"] = f"Bearer {new_access_token}"
                response = SESSION.request(
                    method=method,
                    url=url,
                    data=data,
                    json=json,
                    headers=headers,
                    **kwargs
                )

    return response
