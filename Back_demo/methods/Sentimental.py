from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax
import pandas as pd

def Sentimental(tweet):
    # Cambia el modelo a uno adecuado para español
    MODEL = "nlptown/bert-base-multilingual-uncased-sentiment"
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL)
    # Lee el archivo CSV
    df = tweet
    # Asignación de valores a las etiquetas de sentimiento
    sentiment_labels = [-2, -1, 0, 1, 2]
    # Función para calcular la puntuación de sentimiento
    def calculate_sentiment(text):
        inputs = tokenizer(text, return_tensors="pt")
        outputs = model(**inputs)
        scores = outputs.logits.detach().numpy()
        scores = softmax(scores[0])
        sentiment_score = sum([a*b for a, b in zip(sentiment_labels, scores)])
        return sentiment_score

    # Aplicar la función a cada texto en la columna 'Texto'
    df['Puntaje'] = df['Texto'].apply(calculate_sentiment)



    # Guardar el dataset modificado en un nuevo archivo CSV
    return df.reset_index(drop=True)