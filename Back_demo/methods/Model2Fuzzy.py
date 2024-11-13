##################################
# Library for using a spacy trained model and compare words with possible matches using fuzzy 
# Use it with wiseness
import spacy
import pandas as pd
import unicodedata
import ast
import regex as re
from fuzzywuzzy import fuzz, process
# Receives a spacy model, an initial dataframe to analyse text
# labels of spacy detection to analyse and the name of the output
def CreateLabels(model, dataframe, colName ,labels):
    print("Creating labels")
    model = spacy.load(model)
    df = dataframe.drop_duplicates().dropna(subset=[colName]).reset_index(drop=True)
    new_df = df.copy() #Creates a copy of this new dataframe
   # Cycle to go through each tweet in the dataframe
    for idx, tweet in enumerate(new_df[colName]):
        info = {label: [] for label in labels}  # Create the current dictionary
        doc = model(tweet) #Identify entities
        #Cycle to go through each entity recognised
        for ent in doc.ents:  
            # We only want the labels in labels COL, MUN, etc
            if ent.label_ in labels:
                info[ent.label_].append(ent.text) #Add the label and the tweet in the dictionary
        # Now with the dictionary we will crate the last dataframe
        # Cycle to go through each key and value of the dictionary
        for label, values in info.items():
            #If there is no entity 
            if values == []: 
                values = "" #Empty string
            else:
                # If there is more tahn one entity make a string chain
                values = ', '.join(values) 
            #Add to dataframe
            new_df.at[idx, label] = values 
        # Save dataframe after all the process  (NOT NECESARY)
    print("Labels created")

    return new_df.reset_index(drop=True)

# Normalize a text
def normalize_prefixes(entity):
    entity = entity.lower()  # Ignorar mayúsculas/minúsculas
    entity = unicodedata.normalize('NFKD', entity).encode('ascii', 'ignore').decode('ascii') #Ignore accetns
    # Reemplazar prefijos solo si están al inicio
    entity = re.sub(r"^avenida( |$)", "", entity)
    entity = re.sub(r"^avenida(|$)", "", entity)
    entity = re.sub(r"^ave( |$)", "", entity)
    entity = re.sub(r"^ave(|$)", "", entity)
    entity = re.sub(r"^av( |$)", "", entity)  # Reemplaza 'av' o 'ave' al inicio
    entity = re.sub(r"^av(|$)", "", entity)  # Reemplaza 'av' o 'ave' al inicio
    entity = re.sub(r"^colonia( |$)", "", entity)
    entity = re.sub(r"^colonia(|$)", "", entity)
    entity = re.sub(r"^col( |$)", "", entity)  # Elimina el prefijo 'col' o 'colonia'
    entity = re.sub(r"^col(|$)", "", entity)  # Elimina el prefijo 'col' o 'colonia'
    entity = re.sub(r"^municipio( |$)", "", entity)
    entity = re.sub(r"^municipio(|$)", "", entity)
    entity = re.sub(r"^mun( |$)", "", entity)
    entity = re.sub(r"^mun(|$)", "", entity)
    entity = re.sub(r"^calle( |$)", "", entity)
    entity = re.sub(r"^calle(|$)", "", entity)
    entity = re.sub(r"^boulevard( |$)", "", entity)
    entity = re.sub(r"^boulevard(|$)", "", entity)
    entity = re.sub(r"^blvd( |$)", "", entity)
    entity = re.sub(r"^blvd(|$)", "", entity)
    entity = re.sub(r"^calzada( |$)", "", entity)
    entity = re.sub(r"^calzada(|$)", "", entity)
    entity = re.sub(r"^privada( |$)", "", entity)
    entity = re.sub(r"^privada(|$)", "", entity)
    entity = re.sub(r"^paseo( |$)", "", entity)
    entity = re.sub(r"^paseo(|$)", "", entity)
    
    entity = entity.replace(".", "")
    entity = entity.replace(" ", "")  # Eliminar puntos
    return entity.strip()  # Eliminar espacios en blanco innecesarios

# Find similar words with the dataframe
# Find Entity in dataframe in the column etiqueta
def find_best_coincidence(entity, df, etiqueta):
    # Normalizar los nombres en la base de datos antes de comparar
    normalized_names = [normalize_prefixes(name) for name in df[etiqueta] if pd.notna(name)] #normaliza la base de datos
    real_names = [name for name in df[etiqueta] if pd.notna(name)]
    # Find best coincidence and score
    best_coincidence, score = process.extractOne(entity, normalized_names, scorer=fuzz.token_sort_ratio)
    # Extract the index
    idx = normalized_names.index(best_coincidence)
    return best_coincidence, score, idx, real_names[idx]

def Fuzzy2Result(ExpData, RealData, labels):
    quantity = 0
    print("Analyzing coincidences")
    obtainedData = ExpData
    obtainedData = obtainedData.rename(columns={'COL': 'colonia', 'CALLE': 'calle', 'MUN': 'municipio'})
    locationData = RealData
    colIterableNames = labels
    fuzzyDataFrame = obtainedData.copy()
    #Iterate thorugh the important labels
    for label in colIterableNames:
        for idx, entity in obtainedData[label].items(): 
            #if the entity is empty
            if pd.isna(entity) or entity == "[]":
                continue #Exit the iteration
            #Initialize coincidence array
            coincidences = []
            #If a list is in a weird format it convert it to string
            try:
                convertLists = ast.literal_eval(entity)     
            except (ValueError, SyntaxError):
                convertLists = entity.split(",") #Transform the list in strings 

            for name in convertLists:
                ## Normalizar las palabras a un estandar
                normalized_Name = normalize_prefixes(name)
                if normalized_Name == '':
                    continue
                # SPECFICIC EXCEPTIONS
                # Normalizar el nombre de la colonia antes de comparar
                if label == "municipio":
                    if normalized_Name == "spgg" or normalized_Name == "sanpedro" or normalized_Name == "sp":
                        normalized_Name = "sanpedrogarzagarcía"
                    elif normalized_Name == "mty":
                        normalized_Name = "monterrey"
                    elif normalized_Name == "gpe":
                        normalized_Name = "guadalupe"
                elif label == "calle":
                    if normalized_Name == "garzasada":
                        normalized_Name = "eugeniogarzasada"
                    elif normalized_Name == "pinosuarez":
                        normalized_Name = "josemariapinosuarez"
                    elif normalized_Name == "moronesprieto":
                        normalized_Name = "manuelmoronesprieto"
                    elif normalized_Name == "lopezmateos":
                        normalized_Name = "adolfolopezmateos"              
                ##Find the best math based on the porcentage
                best_coincidence, score, idx_name, real_name = find_best_coincidence(normalized_Name, locationData, label)
                # If the porcetenge is enough
                if score > 60:
                    quantity += 1
                    # Add the similar word 
                    coincidences.append(real_name)
                    ## EXCEPTION| If it detects a colony it wil add its .shape
                    # if label == "colonia":
                    #     fuzzyDataFrame.loc[idx, 'geometría'] = locationData.iloc[idx_name]['geometry']  # Add geometry
                        # Print the new word and the replaced one
                    print(f"Fila {idx}: Reemplazando '{normalized_Name}' por '{real_name}' con {score}% de similitud")
                        #fuzzyDataFrame = pd.concat([fuzzyDataFrame, obtainedData.loc[[idx]]])  # Añadir la fila actualizada
                else:
                    print(f"Fila {idx}: No se encontró coincidencia suficiente para '{normalized_Name}' (Similitud: {score}%)")
                    coincidences.append(None)

                fuzzyDataFrame.loc[idx, label] = ", ".join([x for x in coincidences if x]) if coincidences else np.nan

    print("Process finished. Fuzzy dataframe created.")

    return quantity, fuzzyDataFrame.reset_index(drop=True)
