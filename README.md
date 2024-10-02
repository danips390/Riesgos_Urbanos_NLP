# Riesgos_Urbanos_NLP

## Modelo NER con SPACY
El script ModelV1_0_2 muestra cómo se entrenó un modelo spacy añadiendo mas etiquetas de las que tiene por defecto para diferenciar entre colonias, calles, municipios, estados o localizaciones geográficas. Una vez con el modelo entrenado se utiliza el script Create_spacyDF para visualizar en un histograma las entidades más mencionadas y se crea un dataset donde se añade una columna por entidad y se escribe lo que extrajo por cada etiqueta. Para finalizar el NER se ocupó un modelo de rapidfuzz para buscar semejanza entre palabras por si alguna colonia o municipio estaba mal escrita y se comparó con una base de datos con las colonias reales con su respectiva geometría. 


## Model2Fuzzy library
- CreateLabels(model, dataframe, colName , $\emph{arr[string]}$ labels, string dataframeOutputName):
