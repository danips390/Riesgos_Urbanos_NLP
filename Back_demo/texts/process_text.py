import json
from uuid import uuid4
from paths import ENCODING, USER_RECORD, MTY_DF, TWEETS_STORAGE, FUZY_PATH, CLASSIFY_PATH, CLASS_LABELS, MUN_PATH, COL_PATH
from methods import Model2Fuzzy as mf
from methods import Classify as cs
from methods import Sentimental as ss
import pandas as pd
import os

def _save_tweet(tweet_record: str) -> None:
    # Guardar el registro de tweets actualizado
    with open(USER_RECORD, "w", encoding=ENCODING) as file:
        json.dump({"tweets": tweet_record}, file, ensure_ascii=False, indent=4)

def process_text_storage(text: str) -> bool:
    print("Analizando texto")
    with open(USER_RECORD, "r", encoding=ENCODING) as file:
        tweet_record = json.load(file)["tweets"]
    # Asignar un nuevo UUID como clave y el texto como valor
    uid = str(uuid4())
    tweet_record[uid] = text
    _save_tweet(tweet_record)  # Almacena el texto con UUID
    print("Texto almacenado correctamente")
    ## ----------------------------------------------------------- Proceso de analisis de tweets
    entidades_identificadas, temp_df = CreateLabelsAndFDF(text)
    if entidades_identificadas <= 0:
        return False
    #Pasamos el tweet ya con labels y con fuzzy
    classified_df = ClassifyText(temp_df)
    #Le damos un valor de riesgo
    processed_tweet = SentimentalAnalysis(classified_df)
    # Guardar en el archivo general
    if os.path.exists(TWEETS_STORAGE):
        general_df = pd.read_csv(TWEETS_STORAGE)
        updated_df = pd.concat([general_df, processed_tweet], ignore_index=True)
    else:
        updated_df = classified_df
        print("General dataframe created")
    
    updated_df.to_csv(TWEETS_STORAGE, index=False)
    print("Proceso completo, datos guardados en: " + TWEETS_STORAGE)
    return True

def CreateLabelsAndFDF(tweet):
    print(tweet)
    # Obtenemos los tweets del JSON para analizar
    df = pd.DataFrame({'Texto': [tweet]})
    lables = ["COL", "CALLE", "MUN", "REGION"]
    print("Creando labels")
    newdf = mf.CreateLabels(FUZY_PATH, df, "Texto", lables)
    print("Labels creadas")
    colIterableNames = ["municipio", "colonia", "calle"]
    realData = pd.read_csv(MTY_DF)
    print("Using Fuzzy")
    quantity, newdf = mf.Fuzzy2Result(newdf, realData, colIterableNames)
    print("Labels creadas")

    return quantity, newdf

def ClassifyText(tweet):
    print("Classifying......")
    # Cargar el tokenizador y el modelo
    class_values = cs.ClassifyTweet(CLASSIFY_PATH,CLASS_LABELS, str(tweet["Texto"]))
    for i in class_values.columns.tolist():
        tweet[i] = class_values[i]
    print("Tweets classified")
    return tweet #Se añaden las columnas de riesgos

def SentimentalAnalysis(tweet):
    print("Sentimental analysis.....")
    tweet = ss.Sentimental(tweet)
    return tweet

def Localize(MUN_PATH, COL_PATH)

