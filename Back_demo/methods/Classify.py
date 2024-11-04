import pandas as pd
import numpy as np
import torch
from transformers import BertTokenizer, BertForSequenceClassification
from sklearn.preprocessing import LabelEncoder
from scipy.special import softmax

def ClassifyTweet(model_path, labels_path, tweet):
    # Cargar el modelo y el tokenizer pre-entrenado
    model = BertForSequenceClassification.from_pretrained(model_path)
    tokenizer = BertTokenizer.from_pretrained(model_path)
    # Tokenizar el texto
    inputs = tokenizer(tweet, return_tensors="pt", padding=True, truncation=True, max_length=128)
    # Asegurarse de que el modelo está en modo de evaluación
    model.eval()
    # Hacer la predicción (no se necesita calcular los gradientes)
    with torch.no_grad():
        outputs = model(**inputs)
    # Obtener las logits y calcular las probabilidades con softmax
    logits = outputs.logits
    probabilidades = softmax(logits.numpy(), axis=1)[0]
    # Cargar el LabelEncoder para obtener las categorías
    df = pd.read_csv(labels_path)
    label_encoder = LabelEncoder()
    df['label'] = label_encoder.fit_transform(df['Tipo'])
    # Obtener los nombres de las categorías
    categorias = label_encoder.classes_
    # Crear un nuevo DataFrame con las categorías y las probabilidades
    df_resultado = pd.DataFrame([probabilidades], columns=categorias)
    # Mostrar el DataFrame con las categorías y sus porcentajes de presencia
    print(df_resultado)
    return df_resultado