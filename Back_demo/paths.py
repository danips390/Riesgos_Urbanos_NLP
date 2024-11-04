"""
Este modulo contiene la constante EXEC_FILES_DIR
"""

from os import path
from uuid import UUID

ENCODING = "utf-8"
USER_RECORD = "tweets.json"
USER_STORAGE = "tweets_storage"
MTY_DF = "databases\DataMTY.csv"
TWEETS_STORAGE = "tweets_storage\storageDF.csv"
FUZY_PATH = r"models\fuzzymodelV1_0_2"
CLASSIFY_PATH = r"models\my_model7"
CLASS_LABELS = "databases\Classification_labels.csv"
MUN_PATH = r"databases\2023_1_19_A\2023_1_19_A.shp"
COL_PATH = r"databases\Colonias\Colonias.shp"

def get_user_path(user_id: UUID) -> str:
    """Retorna el path al directorio del usuario"""
    return path.join(USER_STORAGE, str(user_id))
