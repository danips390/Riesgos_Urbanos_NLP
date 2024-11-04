"""
Este modulo maneja los directorios de los usuarios
"""

import json
import os
import shutil
import uuid
from os import path
from zipfile import ZipFile

from paths import (ENCODING, USER_RECORD, USER_STORAGE,
                   get_user_path)


def assert_user_storage() -> None:
    """TODO
    """
    if not path.exists(USER_RECORD):
        with open(USER_RECORD, "w", encoding=ENCODING) as file:
            user_json = json.dumps({
                "tweets":{}
            })
            file.write(user_json)

    if not path.exists(USER_STORAGE):
        os.mkdir(USER_STORAGE)

#Borrar todos los tweets
def del_user_storage(user_id: uuid.UUID) -> None:
    """Borra el directorio de archivos del usuario especificado"""
    shutil.rmtree(get_user_path(user_id))
