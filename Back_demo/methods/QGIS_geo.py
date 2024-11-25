import pandas as pd
import geopandas as gpd
from geopy.geocoders import Nominatim
import time
from shapely.geometry import Point
import os
import json
import folium
import numpy as np
from matplotlib.colors import Normalize
from matplotlib import cm

def CreateShapeFiles(path_municipios, path_colonias, tweet_storage):
# Inicializar el geolocalizador
    geolocator = Nominatim(user_agent="mi_aplicacion_mapa")
    # Cargar los shapefiles
    shapefile_municipios = path_municipios
    shapefile_colonias = path_colonias
    gdf_municipios = gpd.read_file(shapefile_municipios)
    gdf_colonias = gpd.read_file(shapefile_colonias)
    gdf_colonias = gdf_colonias[gdf_colonias["ST_NAME"] == "NUEVO LEON"]
    # Cargar el archivo CSV
    df_calles = tweet_storage
    df_calles['colonia'] = df_calles['colonia'].str.upper()
    # Crear la columna 'ID' basada en el índice de cada fila
    df_calles['ID'] = df_calles.index

    # Filtrar municipios y calcular puntaje promedio
    cve_mun_values = {
        '006': 'apodaca',
        '019': 'san pedro garza garcía',
        '021': 'escobedo',
        '026': 'guadalupe',
        '039': 'monterrey',
        '046': 'san nicolás',
        '048': 'santa catarina',
        '049': 'santiago'
    }
    promedio_puntajes_municipios = {}
    for cve, municipio in cve_mun_values.items():
        filas_municipio = df_calles[df_calles['municipio'].str.lower() == municipio.lower()]
        if not filas_municipio.empty:
            promedio_puntajes_municipios[cve] = np.mean(filas_municipio['Puntaje'])
        else:
            promedio_puntajes_municipios[cve] = None

    gdf_municipios['Puntaje'] = gdf_municipios['CVE_MUN'].map(promedio_puntajes_municipios)

    # Crear el mapa con Folium
    mapa = folium.Map(location=[25.6866, -100.3161], zoom_start=13)
    municipios_layer = folium.FeatureGroup(name='Municipios')
    colonias_layer = folium.FeatureGroup(name='Colonias')
    calles_layer = folium.FeatureGroup(name='Calles')

    # Añadir municipios al mapa
    norm_municipios = Normalize(vmin=-2, vmax=2)
    cmap_municipios = cm.get_cmap('RdYlGn')

    for _, row in gdf_municipios.iterrows():
        puntaje = row['Puntaje']
        if puntaje is not None:
            color = cmap_municipios(norm_municipios(puntaje))[:3]
            color = [int(c * 255) for c in color]
            folium.GeoJson(
                row['geometry'],
                style_function=lambda x, color=color: {
                    'fillColor': f'rgba({color[0]}, {color[1]}, {color[2]}, 0.6)',
                    'color': 'black',
                    'weight': 1,
                    'fillOpacity': 0.6,
                }
            ).add_to(municipios_layer)

    # Añadir colonias al mapa

    # Convertir los nombres de las colonias en df_calles a mayúsculas
    df_calles['colonia'] = df_calles['colonia'].str.upper()

    # Crear un diccionario para almacenar los promedios de puntajes por colonia
    promedio_puntajes_colonia = {}

    # Obtener la lista de colonias únicas en df_calles
    colonias_unicas = df_calles['colonia'].unique()

    # Calcular el promedio de puntajes para cada colonia
    for colonia in colonias_unicas:
        # Filtrar el DataFrame por la colonia actual
        filas_colonia = df_calles[df_calles['colonia'] == colonia]
        
        if not filas_colonia.empty:
            # Calcular el promedio de puntajes para la colonia
            promedio_puntajes_colonia[colonia] = np.mean(filas_colonia['Puntaje'])
        else:
            # Asignar None si no hay registros para la colonia
            promedio_puntajes_colonia[colonia] = None

    # Asignar estos promedios a df_calles
    df_calles['Promedio_Puntaje'] = df_calles['colonia'].map(promedio_puntajes_colonia)

    # Supongamos que gdf_colonias es tu GeoDataFrame
    # Convertir los nombres de las colonias en gdf_colonias a mayúsculas también (ajusta el nombre de la columna según tu caso)
    gdf_colonias['SETT_NAME'] = gdf_colonias['SETT_NAME'].str.upper()

    # Realizar el merge entre gdf_colonias y df_calles
    promedio_puntajes_colonia = pd.DataFrame(list(promedio_puntajes_colonia.items()), columns=['colonia', 'Puntaje'])
    gdf_colonias = gdf_colonias.merge(promedio_puntajes_colonia, left_on='SETT_NAME', right_on='colonia', how='left')


    gdf_municipios['Puntaje'] = gdf_municipios['CVE_MUN'].map(promedio_puntajes_municipios)
    norm_colonias = Normalize(vmin=df_calles['Puntaje'].min(), vmax=df_calles['Puntaje'].max())
    cmap_colonias = cm.get_cmap('RdYlGn')

    for _, row in gdf_colonias.iterrows():
        puntaje = row['Puntaje']
        if puntaje is not None:
            color = cmap_colonias(norm_colonias(puntaje))[:3]
            color = [int(c * 255) for c in color]
            folium.GeoJson(
                row['geometry'],
                style_function=lambda x, color=color: {
                    'fillColor': f'rgba({color[0]}, {color[1]}, {color[2]}, 0.6)',
                    'color': 'black',
                    'weight': 1,
                    'fillOpacity': 0.4,
                }
            ).add_to(colonias_layer)

    # Añadir capas al mapa
    municipios_layer.add_to(mapa)
    colonias_layer.add_to(mapa)
    folium.LayerControl().add_to(mapa)

    # Guardar archivos SHP
    gdf_municipios.to_file('ArcGis/puntaje_municipios.shp')
    print("Shapefile de municipios creado")
    gdf_colonias.to_file('ArcGis/puntaje_colonias.shp')
    print("Shapefile de colonias creado")

    # Archivo para guardar el último ID procesado
    ultimo_id_file_path = "ultimo_id_procesado.json"

    # Leer el último ID procesado desde el archivo, si existe
    if os.path.exists(ultimo_id_file_path):
        with open(ultimo_id_file_path, 'r') as file:
            ultimo_id_procesado = json.load(file).get('ultimo_id', 0)
    else:
        ultimo_id_procesado = 0
    print("Ultimo ID: " + str(ultimo_id_procesado))
    # Filtrar el DataFrame para obtener solo las filas con ID mayor al último procesado
    df_nuevas_filas = df_calles[df_calles['ID'] > ultimo_id_procesado]
    print(df_calles['ID'])
    # Si hay nuevas filas para procesar
    if not df_nuevas_filas.empty:
        municipios_lista = ['Monterrey', 'Apodaca', 'San Pedro Garza García', 'Escobedo', 'Guadalupe', 'San Nicolás', 'Santa Catarina', 'Santiago']
        datos_geo = []

        for idx, row in df_nuevas_filas.iterrows():
            calles_lista = row['calle']
            puntaje = row['Puntaje']  # Obtener el puntaje de la calle
            tipo = row['Tipo']  # Obtener la clasificación de la calle

            # Asegurarse de que el valor de 'calle' es una cadena
            if isinstance(calles_lista, str):
                calles_lista = [calle.strip() for calle in calles_lista.split(',')]

            # Iterar sobre las calles de la fila
            if isinstance(calles_lista, list) and calles_lista:
                for calle in calles_lista:
                    if calle and "[]" not in calle:  # Asegurarse de que la calle no esté vacía
                        found_location = False
                        for municipio in municipios_lista:
                            try:
                                # Intentar geolocalizar la calle
                                location = geolocator.geocode(calle + ", " + municipio + ", Mexico")
                                time.sleep(1)  # Evitar sobrecarga del servicio
                                if location:
                                    # Guardar los datos geográficos
                                    datos_geo.append({
                                        'calle': calle,
                                        'puntaje': puntaje,
                                        'tipo': tipo,
                                        'geometry': Point(location.longitude, location.latitude)
                                    })
                                    found_location = True
                                    print(f"Se obtuvieron las coordenadas para {calle} en {municipio}")
                                    break
                            except Exception as e:
                                print(f"Error al intentar obtener las coordenadas para {calle} en {municipio}: {e}")                   
                        if not found_location:
                            print(f"No se encontraron coordenadas para {calle} en ningún municipio.")    
        # Convertir los datos de calles nuevas a GeoDataFrame
        gdf_nuevas_calles = gpd.GeoDataFrame(datos_geo, geometry='geometry')
        gdf_nuevas_calles.set_crs(epsg=4326, inplace=True)

        # Verificar si ya existe el archivo SHP anterior
        shp_file_path = 'ArcGis/puntaje_calles.shp'
        
        if os.path.exists(shp_file_path):
            # Si ya existe, cargar los datos antiguos y anexar las nuevas filas
            gdf_calles_existente = gpd.read_file(shp_file_path)
            gdf_calles_actualizado = pd.concat([gdf_calles_existente, gdf_nuevas_calles], ignore_index=True)
        else:
            # Si no existe, simplemente usar las nuevas filas
            gdf_calles_actualizado = gdf_nuevas_calles

        # Guardar el archivo SHP actualizado con los datos anteriores y los nuevos
        gdf_calles_actualizado.to_file(shp_file_path)
        print("Shapefile de calles creado")

    # Actualizar el último ID procesado
        nuevo_ultimo_id = int(df_nuevas_filas['ID'].max())
        try:
            with open(ultimo_id_file_path, 'w') as file:
                json.dump({'ultimo_id': nuevo_ultimo_id}, file)
                file.flush()  # Asegura que los datos se envíen al disco inmediatamente
        except Exception as e:
            print(f"Error al escribir el archivo JSON: {e}")
    else:
        print("No hay nuevas filas para procesar.")
