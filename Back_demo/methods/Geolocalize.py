import folium
import geopandas as gpd
import pandas as pd
import numpy as np
from matplotlib import cm
from matplotlib.colors import Normalize
from geopy.geocoders import Nominatim
import time
import ast
import time 

def CreateMap(path_municipios, path_colonias, tweet):
    ## Start timers
    start_time = time.perf_counter()
    time_measurements = {}
    ########################### MAP CONFIG ######################################
    # Inicializar el geocodificador
    geolocator = Nominatim(user_agent="mi_aplicacion_mapa")
    # Cargar el archivo SHP de municipios
    gdf_municipios = gpd.read_file(path_municipios)
    # Cargar el archivo SHP de colonias
    gdf_colonias = gpd.read_file(path_colonias)
    gdf_colonias = gdf_colonias[gdf_colonias["ST_NAME"] == "NUEVO LEON"]
    # Cargar el DataFrame principal con los datos desde B_testDf.csv
    df_calles = tweet
    # Filtrar los municipios y calcular el puntaje promedio por municipio
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
    mapa = folium.Map(location=[25.6866, -100.3161], zoom_start=13)
     # Crear capas para municipios, colonias y calles
    municipios_layer = folium.FeatureGroup(name='Municipios')
    colonias_layer = folium.FeatureGroup(name='Colonias')
    calles_layer = folium.FeatureGroup(name='Calles')  # Nueva capa para las calles

    time_measurements["MAP CONFIG"] = time.perf_counter() - start_time
    ################################### MUNICIPIOS ###############################################
    load_start = time.perf_counter() 
    promedio_puntajes_municipios = {}
    for cve, municipio in cve_mun_values.items():
        filas_municipio = df_calles[df_calles['municipio'].str.lower() == municipio.lower()]
        if not filas_municipio.empty:
            promedio_puntajes_municipios[cve] = np.mean(filas_municipio['Puntaje'])
        else:
            promedio_puntajes_municipios[cve] = None

    # Asignar los puntajes promedios a los códigos CVE_MUN correspondientes
    gdf_municipios['Puntaje'] = gdf_municipios['CVE_MUN'].map(promedio_puntajes_municipios)

    # Configurar el colormap para municipios
    norm_municipios = Normalize(vmin=-2, vmax=2)
    cmap_municipios = cm.get_cmap('RdYlGn')

    # Añadir los polígonos de municipios al mapa
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
    time_measurements["MUNICIPIOS"] = time.perf_counter() - load_start
    ################################################ COLONIAS #########################################
    load_start = time.perf_counter()
    # Añadir los polígonos de colonias al mapa
    df_calles['colonia'] = df_calles['colonia'].astype(str).str.upper()
    gdf_colonias = gdf_colonias.merge(df_calles, left_on='SETT_NAME', right_on='colonia', how='left')

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

    # Lista de municipios a probar en caso de que no se encuentre la calle en Monterrey
    municipios_lista = ['Monterrey', 'Apodaca', 'San Pedro Garza García', 'Escobedo', 'Guadalupe', 'San Nicolás', 'Santa Catarina', 'Santiago']
    time_measurements["COLONIAS"] = time.perf_counter() - load_start
    ################################################# CALLES ###########################################
    load_start = time.perf_counter()
    # Iterar sobre las calles y listas de calles
    for idx, row in df_calles.iterrows():
        calles_lista = row['calle']
        puntaje = row['Puntaje']  # Obtener el puntaje de la calle
        tipo = row['Tipo']  # Obtener la clasificación de la calle
        
        # Definir el ícono y el color según el tipo de calle
        if tipo.lower() == 'lluvia':
            icono = "cloud"
            color_icono = "blue"
        elif tipo.lower() == 'inundación':
            icono = "tint"
            color_icono = "red"
        elif tipo.lower() == 'eléctrico':
            icono = "flash"  # Cambiado a 'flash' ya que 'plug' no está disponible
            color_icono = "orange"
        else:
            icono = "question-circle"
            color_icono = "gray"  # Color para los tipos no relacionados
        
        # Asegurarse de que el valor de 'calle' es una cadena
        if isinstance(calles_lista, str):
            # Dividir por comas en caso de que haya más de una calle en la celda
            calles_lista = [calle.strip() for calle in calles_lista.split(',')]
        
        # Iterar sobre la lista de calles y geolocalizarlas
        if isinstance(calles_lista, list) and calles_lista:
            for calle in calles_lista:
                if calle:  # Asegurarse de que la calle no esté vacía
                    found_location = False
                    for municipio in municipios_lista:
                        try:
                            # Intentar geolocalizar la calle
                            location = geolocator.geocode(calle + ", " + municipio + ", Mexico")
                            time.sleep(1)  # Evitar sobrecarga del servicio
                            if location:
                                # Crear popup con información de la calle
                                popup_text = f"<b>Calle:</b> {calle}<br><b>Puntaje:</b> {puntaje}<br><b>Clasificación:</b> {tipo}"
                                # Añadir el marcador con el ícono correspondiente
                                folium.Marker(
                                    location=[location.latitude, location.longitude],
                                    popup=popup_text,
                                    icon=folium.Icon(icon=icono, color=color_icono),  # Añadir ícono y color según la clasificación
                                ).add_to(calles_layer)  # Añadir marcador a la capa de calles
                                found_location = True
                                break
                        except Exception as e:
                            print(f"Error al intentar obtener las coordenadas para {calle} en {municipio}: {e}")
                    
                    if not found_location:
                        print(f"No se encontraron coordenadas para {calle} en ningún municipio.")
    time_measurements["CALLES"] = time.perf_counter() - load_start
    ###################################################### ADDING MAPS ##################################################
    load_start = time.perf_counter()
    # Añadir las capas al mapa
    mapa.add_child(municipios_layer)
    mapa.add_child(colonias_layer)
    mapa.add_child(calles_layer)  # Añadir la capa de calles
    # Añadir control de capas
    folium.LayerControl().add_to(mapa)
    # Guardar el mapa como archivo HTML
    #mapa.save("map.html")
    
    mapa_html = mapa._repr_html_()  # Convierte el mapa de folium en un string HTML
    time_measurements["ADDING MAP"] = time.perf_counter() - load_start
    print(time_measurements)
    print("Tiempo total: " + str(time.perf_counter() - start_time))
    return mapa_html
