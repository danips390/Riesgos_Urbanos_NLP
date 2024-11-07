from qgis.core import (
    QgsVectorLayer,
    QgsCategorizedSymbolRenderer,
    QgsGraduatedSymbolRenderer,
    QgsSymbol,
    QgsRendererCategory,
    QgsRendererRange,
    QgsGradientColorRamp,
    QgsSvgMarkerSymbolLayer,
    QgsProject,
    QgsCoordinateReferenceSystem,
    QgsLayerTreeGroup,
    QgsPointXY,
    QgsRasterLayer
)
from PyQt5.QtGui import QColor

# Ruta de los shapefiles
shapefile_municipios = r"C:\Users\ferna\Documents\GitHub\Riesgos_Urbanos_NLP\ArcGis\puntaje_municipios.shp"
shapefile_colonias = r"C:\Users\ferna\Documents\GitHub\Riesgos_Urbanos_NLP\ArcGis\puntaje_colonias.shp"
shapefile_calles = r"C:\Users\ferna\Documents\GitHub\Riesgos_Urbanos_NLP\ArcGis\puntaje_calles.shp"

# Nombre de la columna para la simbología graduada y categórica
columna_graduada = "Puntaje"  # Columna de las primeras dos capas
columna_categoria = "tipo"  # Columna de la tercera capa

# Definir colores de inicio, intermedio y final
color_inicio = QColor('#ff0000')  # Rojo para -2 (inicio, muy alto riesgo)
color_medio_1 = QColor('#ffff00')  # Amarillo para -1 (33% riesgo alto)
color_medio_2 = QColor('#ffa500')  # Naranja para 0 (66% riesgo neutro)
color_fin = QColor('#00913f' )      # Verde para 2 (fin, bajo riesgo)

# Crear rampa de color con puntos intermedios para el 33% y 66%
rampa_color = QgsGradientColorRamp(color_inicio, color_fin)
iconos_svg = {
    "eléctrico": r"C:\Users\ferna\Documents\GitHub\Riesgos_Urbanos_NLP\ArcGis\electric.svg",
    "inundación": r"C:\Users\ferna\Documents\GitHub\Riesgos_Urbanos_NLP\ArcGis\flood.svg",
    "lluvia": r"C:\Users\ferna\Documents\GitHub\Riesgos_Urbanos_NLP\ArcGis\rain.svg",
    "incendio": r"C:\Users\ferna\Documents\GitHub\Riesgos_Urbanos_NLP\ArcGis\fire.svg",
    "problema vial": r"C:\Users\ferna\Documents\GitHub\Riesgos_Urbanos_NLP\ArcGis\traffic.svg",
    "otros": r"C:\Users\ferna\Documents\GitHub\Riesgos_Urbanos_NLP\ArcGis\other.svg"
}


# Crear capas
municipios_layer = QgsVectorLayer(shapefile_municipios, "Municipios", "ogr")
colonias_layer = QgsVectorLayer(shapefile_colonias, "Colonias", "ogr")
calles_layer = QgsVectorLayer(shapefile_calles, "Calles", "ogr")

# Verificar si las capas se cargaron correctamente
if not municipios_layer.isValid() or not colonias_layer.isValid() or not calles_layer.isValid():
    print("Error al cargar las capas.")
else:
    # 1. Aplicar simbología graduada a la primera capa (de rojo a verde)
    simbolo_base = QgsSymbol.defaultSymbol(municipios_layer.geometryType())
    # Obtener el índice de la columna
    # Crear un renderer graduado en modo EqualInterval con 4 clases
    renderer_graduado = QgsGraduatedSymbolRenderer(columna_graduada, [])
    renderer_graduado.setMode(QgsGraduatedSymbolRenderer.EqualInterval)
    renderer_graduado.setClassAttribute(columna_graduada)
    renderer_graduado.updateClasses(municipios_layer, 4)  # Generar 4 intervalos automáticos
    
    limites_rangos = []
    for i, rango in enumerate(renderer_graduado.ranges()):
        # Guardar los límites del rango en el arreglo
        limites_rangos.append((rango.lowerValue(), rango.upperValue()))
    
    rango_1 = QgsRendererRange(limites_rangos[3][0],limites_rangos[3][1], simbolo_base.clone(), "Muy Alto")
    rango_1.symbol().setColor(QColor('#ff0000'))  # Rojo para Muy Alto

    rango_2 = QgsRendererRange(limites_rangos[2][0],limites_rangos[2][1], simbolo_base.clone(), "Alto")
    rango_2.symbol().setColor(QColor('#ff8000'))  # Naranja para Alto

    rango_3 = QgsRendererRange(limites_rangos[1][0],limites_rangos[1][1], simbolo_base.clone(), "Neutro")
    rango_3.symbol().setColor(QColor('#ffff00'))  # Amarillo para Neutro

    rango_4 = QgsRendererRange(limites_rangos[0][0],limites_rangos[0][1], simbolo_base.clone(), "Bajo")
    rango_4.symbol().setColor(QColor('#00913f'))  # Verde para Bajo
    # Configurar el renderer con los rangos específicos
    renderer_graduado = QgsGraduatedSymbolRenderer(columna_graduada, [rango_1, rango_2, rango_3, rango_4])
    renderer_graduado.setMode(QgsGraduatedSymbolRenderer.EqualInterval)
    # Asignar el renderer a la capa
    municipios_layer.setRenderer(renderer_graduado)
    # # Asignar el renderer a la capa
    municipios_layer.setRenderer(renderer_graduado)
    municipios_layer.setOpacity(0.6)

    # 2. Aplicar simbología graduada a la segunda capa (de rojo a verde)
    simbolo_base = QgsSymbol.defaultSymbol(colonias_layer.geometryType())
    # Obtener el índice de la columna
    columna_index = colonias_layer.fields().indexFromName(columna_graduada)

    rango_1 = QgsRendererRange(-2, -1, simbolo_base.clone(), "Muy Alto")
    rango_1.symbol().setColor(QColor('#ff0000'))  # Rojo para Muy Alto

    rango_2 = QgsRendererRange(-1, 0, simbolo_base.clone(), "Alto")
    rango_2.symbol().setColor(QColor('#ff8000'))  # Naranja para Alto

    rango_3 = QgsRendererRange(0, 1, simbolo_base.clone(), "Neutro")
    rango_3.symbol().setColor(QColor('#ffff00'))  # Amarillo para Neutro

    rango_4 = QgsRendererRange(1, 2, simbolo_base.clone(), "Bajo")
    rango_4.symbol().setColor(QColor('#00913f'))  # Verde para Bajo
    # Configurar el renderer con los rangos específicos
    renderer_graduado_2 = QgsGraduatedSymbolRenderer(columna_graduada, [rango_1, rango_2, rango_3, rango_4])
    renderer_graduado_2.setMode(QgsGraduatedSymbolRenderer.EqualInterval)
    
    # Asignar el renderer a la capa
    colonias_layer.setRenderer(renderer_graduado_2)
    colonias_layer.setOpacity(0.6)

    # 3. Aplicar simbología de iconos SVG categorizados a la tercera capa
    categorias = []
    valores = calles_layer.dataProvider().uniqueValues(calles_layer.fields().lookupField(columna_categoria))

    for valor in valores:
        simbolo = QgsSymbol.defaultSymbol(calles_layer.geometryType())
        
        # Obtener la ruta del icono según el valor de la categoría usando un diccionario (simulando switch-case)
        ruta_icono = iconos_svg.get(valor.lower(), iconos_svg["otros"])  # Usar "otros" como icono por defecto si el tipo no se encuentra
        
        # Crear la capa de marcador SVG
        svg_layer = QgsSvgMarkerSymbolLayer(ruta_icono, 4.0, 0)  # tamaño
        simbolo.changeSymbolLayer(0, svg_layer)
        
        # Agregar la categoría al renderer
        categorias.append(QgsRendererCategory(valor, simbolo, str(valor)))

    # Crear y asignar el renderer categorizado
    renderer_categorico = QgsCategorizedSymbolRenderer(columna_categoria, categorias)
    calles_layer.setRenderer(renderer_categorico)

    # Añadir las capas al proyecto actual
    QgsProject.instance().addMapLayer(municipios_layer)
    QgsProject.instance().addMapLayer(colonias_layer)
    QgsProject.instance().addMapLayer(calles_layer)

    print("Capas cargadas y simbología aplicada correctamente.")
