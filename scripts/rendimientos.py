"""Rendimientos de referencia por actividad.

El export de Construbase no trae las matrices de precios unitarios, así que
no incluye rendimientos. Esta tabla asigna a cada concepto un rendimiento
típico de la práctica mexicana (cuadrilla y unidades por jornada de 8 h),
tomado de referencias usuales de costos de edificación. Son valores de
arranque y se deben validar con las matrices de Construbase o con datos de obra.

Cada concepto se asocia a una "familia" de actividad mediante reglas
(capítulo, subcapítulo, descripción). La familia y la unidad del concepto
determinan la fila de la tabla. En tuberías, ductos y conexiones, el diámetro
cambia el rendimiento (sufijo "g" para diámetros grandes).
"""
import re

from reglas_gubim import normalizar

# Cuadrillas: personas y costo por jornada en 2017 (salario real con FSR,
# valores de referencia editables en la hoja "Cuadrillas" del Excel).
CUADRILLAS = {
    #  clave     descripción                          personas  costo 2017
    "Pe":     ("1 peón",                                 1,   420.0),
    "2Pe":    ("2 peones",                               2,   840.0),
    "Of":     ("1 oficial",                              1,   750.0),
    "Of+Pe":  ("1 oficial + 1 peón",                     2,  1170.0),
    "Of+Ay":  ("1 oficial + 1 ayudante",                 2,  1230.0),
    "Of+2Pe": ("1 oficial + 2 peones",                   3,  1590.0),
    "Of+5Pe": ("1 oficial + 5 peones (colados)",         6,  2850.0),
    "Top":    ("1 topógrafo + 2 cadeneros",              3,  1840.0),
    "Eq":     ("Equipo con operador (rendimiento de máquina)", 1, None),
}

# (familia, unidad, tamaño) -> (descripción, cuadrilla, rendimiento u/jornada)
_T = [
    # Preliminares y demoliciones
    ("trazo_manual", "M2", "", "Trazo y nivelación manual", "Of+Pe", 250),
    ("trazo_topo", "M2", "", "Trazo y nivelación con equipo topográfico", "Top", 600),
    ("trazo_topo", "M", "", "Trazo y nivelación de ejes de tubería", "Top", 500),
    ("tapial", "M", "", "Tapial de obra", "Of+Pe", 12),
    ("limpia", "M2", "", "Limpia y desyerbe del terreno", "Pe", 120),
    ("tala", "PZA", "", "Tala de árbol hasta 20 cm de diámetro", "2Pe", 8),
    ("tala", "PZA", "g", "Tala de árbol mayor a 20 cm de diámetro", "2Pe", 2.5),
    ("desmonte", "HA", "", "Desmonte y desenraice con maquinaria", "Eq", 1.5),
    ("sanitario", "MES", "", "Renta mensual de sanitario portátil", "Eq", 1),
    ("demolicion", "M3", "", "Demolición de elementos de concreto/mampostería", "2Pe", 1.5),
    ("demolicion", "M2", "", "Demolición de recubrimientos, pisos o muros", "Pe", 20),
    ("demolicion", "M", "", "Demolición de elementos lineales", "Pe", 20),
    ("demolicion", "PZA", "", "Demolición de piezas", "Pe", 6),
    ("demolicion", "KG", "", "Demolición/retiro de elementos metálicos", "Of+Ay", 250),
    ("desmontaje", "PZA", "", "Desmontaje de piezas y accesorios", "Of+Ay", 20),
    ("desmontaje", "PZA", "g", "Desmontaje de equipo o pieza pesada", "Of+Ay", 3),
    ("desmontaje", "M", "", "Desmontaje de tubería, cable o elementos lineales", "Of+Ay", 60),
    ("desmontaje", "M2", "", "Desmontaje de recubrimientos, plafones o cubiertas", "Of+Ay", 40),
    ("desmontaje", "KG", "", "Desmontaje de estructura metálica", "Of+Ay", 250),
    ("desmontaje", "SAL", "", "Desmontaje de salida eléctrica o hidráulica", "Of+Ay", 20),
    ("desmontaje", "PT", "", "Desmontaje de viga de madera (pie-tablón)", "Of+Ay", 150),
    ("descableado", "M", "", "Descableado de instalación eléctrica", "Of+Ay", 400),
    # Movimiento de tierras
    ("exc_manual", "M3", "", "Excavación por medios manuales", "Pe", 3.5),
    ("exc_maquina", "M3", "", "Excavación o corte con maquinaria", "Eq", 200),
    ("exc_martillo", "M3", "", "Excavación en roca con martillo hidráulico", "Eq", 25),
    ("afine", "M2", "", "Afine y compactación manual de fondo", "Pe", 60),
    ("relleno_manual", "M3", "", "Relleno compactado con pisón de mano", "Pe", 4),
    ("relleno_volteo", "M3", "", "Relleno a volteo", "Pe", 12),
    ("relleno_equipo", "M3", "", "Relleno o terraplén compactado con equipo", "Eq", 120),
    ("mejoramiento", "M2", "", "Mejoramiento de terreno con equipo", "Eq", 600),
    ("mejoramiento", "M3", "", "Mejoramiento de material con equipo", "Eq", 150),
    ("acarreo_manual", "M3", "", "Acarreo en carretilla, bote o costal (1a estación)", "Pe", 6),
    ("acarreo_manual", "M3/E", "", "Acarreo manual, estación subsecuente", "Pe", 12),
    ("elevacion", "M3", "", "Elevación de materiales", "2Pe", 6),
    ("carga_mano", "M3", "", "Carga a mano de material", "Pe", 8),
    ("acarreo_camion", "M3", "", "Carga mecánica y acarreo en camión", "Eq", 120),
    ("acarreo_camion", "M3/KM", "", "Acarreo en camión, km subsecuente", "Eq", 400),
    ("acarreo_camion", "VIAJE", "", "Viaje de camión con carga manual", "2Pe", 2),
    ("bombeo", "HR", "", "Bombeo de achique", "Eq", 8),
    # Concreto, acero, cimbra
    ("plantilla", "M2", "", "Plantilla de concreto", "Of+2Pe", 40),
    ("concreto", "M3", "", "Concreto hecho en obra: colado y vibrado", "Of+5Pe", 10),
    ("concreto", "M3", "g", "Concreto premezclado o bombeado: colado y vibrado", "Of+5Pe", 25),
    ("acero", "KG", "", "Acero de refuerzo: habilitado y armado", "Of+Ay", 250),
    ("acero", "TON", "", "Acero de refuerzo: habilitado y armado", "Of+Ay", 0.25),
    ("malla", "M2", "", "Malla electrosoldada", "Of+Ay", 100),
    ("cimbra", "M2", "", "Cimbra acabado común", "Of+Ay", 10),
    ("cimbra", "M2", "g", "Cimbra acabado aparente", "Of+Ay", 7),
    ("cimbra", "M", "", "Cimbra con sonotubo", "Of+Ay", 8),
    ("curado", "M2", "", "Curado o polietileno", "Pe", 150),
    ("pulido", "M2", "", "Pulido integral de concreto a máquina", "Of+Pe", 60),
    ("cimiento_piedra", "M", "", "Cimiento de piedra braza", "Of+2Pe", 3),
    ("cimiento_piedra", "M3", "", "Cimiento de piedra braza", "Of+2Pe", 1.8),
    ("pepena", "M3", "", "Pepena de piedra", "Pe", 3),
    ("cimiento_concreto", "M", "", "Zapata corrida de concreto armado", "Of+5Pe", 6),
    ("cimiento_concreto", "PZA", "", "Zapata aislada de concreto armado", "Of+5Pe", 1.5),
    ("elemento_concreto", "M", "", "Columna, trabe o contratrabe de concreto armado", "Of+2Pe", 4),
    ("muro_contencion", "M", "", "Muro de contención de concreto armado", "Of+5Pe", 2),
    ("losa", "M2", "", "Losa de concreto armado", "Of+5Pe", 15),
    ("losa_vigueta", "M2", "", "Losa de vigueta y bovedilla o panel", "Of+2Pe", 25),
    # Estructura metálica y cubiertas
    ("est_metalica", "KG", "", "Estructura metálica: fabricación y montaje", "Of+Ay", 180),
    ("est_metalica", "TON", "", "Estructura metálica: fabricación y montaje", "Of+Ay", 0.18),
    ("est_metalica", "PZA", "", "Placa o pieza metálica", "Of+Ay", 8),
    ("grout", "M3", "", "Asentamiento de placas con grout", "Of+Pe", 0.5),
    ("cubierta_lamina", "M2", "", "Cubierta o muro de lámina", "Of+Ay", 40),
    ("cubierta_lamina", "PZA", "", "Pieza en cubierta (extractor, domo)", "Of+Ay", 4),
    ("cubierta_lamina", "M", "", "Caballete o remate de lámina", "Of+Ay", 30),
    # Albañilería
    ("mezcla", "M3", "", "Elaboración de mezcla o concreto en obra", "2Pe", 2),
    ("muro_tabique", "M2", "", "Muro de tabique o tabicón", "Of+Pe", 8),
    ("muro_tabique", "M", "", "Muro o mocheta de tabique por metro", "Of+Pe", 6),
    ("muro_block", "M2", "", "Muro de block", "Of+Pe", 12),
    ("muro_piedra", "M2", "", "Muro de piedra braza", "Of+2Pe", 3),
    ("muro_piedra", "M3", "", "Mampostería de piedra braza", "Of+2Pe", 1.8),
    ("muro_covintec", "M2", "", "Muro de panel covintec", "Of+Ay", 15),
    ("cadena", "M", "", "Cadena, dala o castillo de concreto", "Of+Pe", 8),
    ("aplanado", "M2", "", "Aplanado en muros", "Of+Pe", 14),
    ("aplanado", "M2", "g", "Aplanado en plafones", "Of+Pe", 10),
    ("aplanado", "M", "", "Boquilla o remate de aplanado", "Of+Pe", 25),
    ("firme", "M2", "", "Firme o piso de concreto", "Of+2Pe", 30),
    ("registro", "PZA", "", "Registro de albañilería", "Of+Pe", 1),
    ("tubo_concreto", "M", "", "Tubo de concreto asentado", "Of+Pe", 15),
    ("cama_arena", "M", "", "Cama de arena para tubería", "Pe", 30),
    ("cama_arena", "M3", "", "Cama de arena", "Pe", 4),
    ("escalon", "M", "", "Escalones de concreto o tabique", "Of+Pe", 8),
    ("escalon", "PZA", "", "Escalón metálico de escalera marina", "Of+Ay", 12),
    ("azotea", "M2", "", "Relleno, entortado o enladrillado en azotea", "Of+Pe", 30),
    ("azotea", "M3", "", "Relleno de tezontle en azotea", "Pe", 4),
    ("azotea", "M", "", "Chaflán o sardinel", "Of+Pe", 30),
    ("lavadero", "PZA", "", "Lavadero de concreto", "Of+Pe", 2),
    ("imper", "M2", "", "Impermeabilización", "Of+Ay", 40),
    ("imper", "M", "", "Impermeabilización en desplante de muros", "Of+Ay", 80),
    # Muros y plafones de panel
    ("muro_panel", "M2", "", "Muro de panel de yeso o cemento", "Of+Ay", 12),
    ("muro_panel", "M2", "g", "Muro doble, curvo o murete de panel", "Of+Ay", 8),
    ("muro_panel", "M", "", "Forro de columna o cajillo de panel", "Of+Ay", 8),
    ("plafon_panel", "M2", "", "Falso plafón de panel", "Of+Ay", 14),
    ("plafon_panel", "M", "", "Remate o registro lineal en plafón", "Of+Ay", 15),
    ("plafon_modular", "M2", "", "Falso plafón modular", "Of+Ay", 30),
    # Acabados
    ("loseta_vinilica", "M2", "", "Loseta vinílica", "Of+Ay", 35),
    ("zoclo", "M", "", "Zoclo o nariz de escalón", "Of", 40),
    ("zoclo", "M2", "", "Zoclo medido por m2", "Of+Ay", 10),
    ("ceramico", "M2", "", "Piso o azulejo cerámico", "Of+Ay", 10),
    ("mosaico", "M2", "", "Mosaico veneciano", "Of+Ay", 5),
    ("piedra_natural", "M2", "", "Mármol, granito o cantera", "Of+Ay", 6),
    ("piedra_natural", "M", "", "Pieza lineal de mármol, granito o cantera", "Of+Ay", 10),
    ("piedra_natural", "PZA", "", "Cubierta o pieza de mármol", "Of+Ay", 2),
    ("piedra_natural", "KG", "", "Material pétreo a granel", "Pe", 500),
    ("piedra_natural", "M3", "", "Material pétreo", "2Pe", 3),
    ("pintura", "M2", "", "Pintura", "Of", 60),
    ("pintura", "M", "", "Pintura en elementos lineales", "Of", 80),
    ("pintura", "PZA", "", "Pintura de pieza", "Of", 10),
    ("pintura", "KG", "", "Pintura de estructura metálica por kg", "Of+Ay", 600),
    ("pasta", "M2", "", "Pasta o recubrimiento texturizado", "Of", 25),
    ("alfombra", "M2", "", "Alfombra", "Of+Ay", 50),
    ("alfombra", "M", "", "Remate de alfombra", "Of", 60),
    # Herrería, aluminio, vidrio
    ("herreria", "PZA", "", "Pieza de herrería (puerta, tapa, protección)", "Of+Ay", 1.5),
    ("herreria", "PZA", "g", "Pieza grande de herrería (escalera, portón)", "Of+Ay", 0.4),
    ("herreria", "M", "", "Herrería lineal (cerca, barandal, reja)", "Of+Ay", 12),
    ("herreria", "M2", "", "Herrería por superficie (rejilla, reja)", "Of+Ay", 6),
    ("aluminio", "PZA", "", "Ventana o cancel de aluminio", "Of+Ay", 3),
    ("aluminio", "PZA", "g", "Puerta, cancel grande o portón de aluminio", "Of+Ay", 1),
    ("aluminio", "M2", "", "Cristal, celosía o cancelería por m2", "Of+Ay", 10),
    ("domo", "PZA", "", "Domo", "Of+Ay", 4),
    # Carpintería
    ("carpinteria", "PZA", "", "Puerta de madera", "Of+Ay", 2),
    ("carpinteria", "PZA", "g", "Closet o mueble de carpintería", "Of+Ay", 0.5),
    ("carpinteria", "M2", "", "Piso de duela, parquet o lambrín", "Of+Ay", 8),
    ("carpinteria", "M", "", "Zoclo de madera", "Of", 40),
    # Muebles de baño y cocina
    ("mueble_sanitario", "PZA", "", "Mueble sanitario, tarja o equipo menor", "Of+Ay", 3),
    ("mueble_sanitario", "PZA", "g", "Tina, tinaco, cisterna o equipo de bombeo", "Of+Ay", 1),
    ("mueble_sanitario", "JGO", "", "Juego de muebles o mamparas", "Of+Ay", 1),
    ("accesorio", "PZA", "", "Accesorio, llave o grifería", "Of", 8),
    ("accesorio", "JGO", "", "Juego de accesorios", "Of", 4),
    ("mampara", "PZA", "", "Mampara sanitaria", "Of+Ay", 1),
    ("mampara", "JGO", "", "Juego de mamparas", "Of+Ay", 1),
    # Instalaciones hidrosanitarias y contra incendio
    ("tuberia", "M", "", "Tubería hasta 38 mm", "Of+Ay", 30),
    ("tuberia", "M", "g", "Tubería mayor a 38 mm", "Of+Ay", 15),
    ("tuberia", "PZA", "", "Tramo de tubo hasta 38 mm", "Of+Ay", 12),
    ("tuberia", "PZA", "g", "Tramo de tubo de fierro fundido mayor a 38 mm", "Of+Ay", 6),
    ("conexion", "PZA", "", "Conexión hasta 38 mm", "Of+Ay", 50),
    ("conexion", "PZA", "g", "Conexión mayor a 38 mm", "Of+Ay", 15),
    ("valvula", "PZA", "", "Válvula hasta 38 mm", "Of+Ay", 10),
    ("valvula", "PZA", "g", "Válvula mayor a 38 mm", "Of+Ay", 4),
    ("coladera", "PZA", "", "Coladera o fluxómetro", "Of+Ay", 4),
    ("salida", "SAL", "", "Salida hidrosanitaria", "Of+Ay", 2),
    ("salida", "M", "", "Línea hidráulica", "Of+Ay", 15),
    ("salida", "PZA", "", "Salida o línea hidráulica", "Of+Ay", 2),
    ("soporte", "PZA", "", "Soporte o taquete de expansión", "Of+Ay", 50),
    ("prueba", "M", "", "Prueba hidrostática", "Of+Ay", 300),
    ("atraque", "PZA", "", "Atraque de concreto", "Of+Pe", 8),
    ("pozo", "PZA", "", "Pozo de visita o brocal", "Of+2Pe", 0.5),
    # Instalación eléctrica
    ("conduit", "M", "", "Tubería conduit hasta 27 mm", "Of+Ay", 60),
    ("conduit", "M", "g", "Tubería conduit mayor a 27 mm", "Of+Ay", 30),
    ("conduit", "PZA", "", "Accesorio de conduit hasta 27 mm", "Of+Ay", 80),
    ("conduit", "PZA", "g", "Accesorio de conduit mayor a 27 mm", "Of+Ay", 40),
    ("conduit", "JGO", "", "Juego de contra y monitor", "Of+Ay", 80),
    ("cable", "M", "", "Cable hasta cal. 8", "Of+Ay", 200),
    ("cable", "M", "g", "Cable cal. 6 o mayor", "Of+Ay", 80),
    ("tablero", "PZA", "", "Interruptor termomagnético", "Of", 12),
    ("tablero", "PZA", "g", "Centro de carga o tablero", "Of+Ay", 2),
    ("salida_electrica", "SAL", "", "Salida eléctrica", "Of+Ay", 4),
    ("salida_electrica", "PZA", "", "Salida eléctrica por pieza", "Of+Ay", 4),
    ("salida_electrica", "M", "", "Línea de alimentación eléctrica", "Of+Ay", 20),
    # Aire acondicionado
    ("difusor", "PZA", "", "Difusor, rejilla o compuerta", "Of+Ay", 10),
    ("ducto", "KG", "", "Ducto de lámina galvanizada", "Of+Ay", 80),
    ("ducto", "M", "", "Ducto circular hasta 16\"", "Of+Ay", 15),
    ("ducto", "M", "g", "Ducto circular mayor a 16\"", "Of+Ay", 8),
    ("ducto", "PZA", "", "Pieza de ducto hasta 24\"", "Of+Ay", 15),
    ("ducto", "PZA", "g", "Pieza de ducto mayor a 24\"", "Of+Ay", 4),
    ("ducto", "M2", "", "Conexión flexible de lona", "Of+Ay", 10),
    ("aislamiento", "M", "", "Aislamiento térmico de tubería", "Of+Ay", 30),
    ("aislamiento", "M2", "", "Aislamiento térmico por m2", "Of+Ay", 25),
    ("equipo_hvac", "PZA", "", "Equipo de aire acondicionado hasta 5 ton", "Of+Ay", 1),
    ("equipo_hvac", "PZA", "g", "Equipo de aire acondicionado mayor a 5 ton", "Of+Ay", 0.25),
    # Limpieza y jardinería
    ("limpieza", "PZA", "", "Limpieza de pieza", "Pe", 25),
    ("limpieza", "M2", "", "Limpieza de superficie", "Pe", 80),
    ("limpieza", "JGO", "", "Limpieza de juego de piezas", "Pe", 10),
    ("jardineria", "PZA", "", "Planta en jardín", "Pe", 25),
    ("jardineria", "M2", "", "Pasto", "Pe", 40),
    ("jardineria", "M3", "", "Tierra vegetal", "Pe", 4),
    # Urbanización
    ("base", "M3", "", "Base, sub-base o terraplén con equipo", "Eq", 150),
    ("riego_asfalto", "M2", "", "Riego asfáltico o areneado", "Eq", 3000),
    ("carpeta", "M2", "", "Carpeta asfáltica", "Eq", 800),
    ("pavimento_concreto", "M2", "", "Tendido de pavimento hidráulico", "Of+5Pe", 60),
    ("pavimento_concreto", "M3", "", "Suministro de concreto", "Eq", 60),
    ("pavimento_concreto", "M", "", "Calafateo de juntas", "Of+Pe", 200),
    ("banqueta", "M2", "", "Banqueta de concreto", "Of+2Pe", 25),
    ("banqueta", "M", "", "Guarnición de concreto", "Of+2Pe", 15),
    ("mo_lote", "PT", "", "Partida global", "Eq", 1),
]
ACTIVIDADES = {(f, u, t): (d, c, r) for f, u, t, d, c, r in _T}

# Reglas (capítulo, subcapítulo, descripción) -> familia, en orden.
_R = [
    (None, None, r"^trazo.*manual", "trazo_manual"),
    (None, None, r"^trazo", "trazo_topo"),
    (None, None, r"^tapial", "tapial"),
    (None, None, r"sanitario portatil", "sanitario"),
    (None, None, r"^(limpia|desyerbe)", "limpia"),
    (None, None, r"^tala", "tala"),
    (None, None, r"^desmonte", "desmonte"),
    (None, r"demoliciones", None, "demolicion"),
    (None, None, r"^descableado", "descableado"),
    (None, r"desmontajes", None, "desmontaje"),
    (None, None, r"^(excavacion|corte de terreno|despalme).*(martillo)", "exc_martillo"),
    (None, None, r"^(excavacion|corte de terreno|despalme).*(manual|a mano)", "exc_manual"),
    (None, None, r"^(excavacion|corte de terreno|despalme)", "exc_maquina"),
    (None, None, r"^afine", "afine"),
    (None, None, r"^relleno a volteo", "relleno_volteo"),
    (None, None, r"^relleno.*tezontle", "azotea"),
    (None, None, r"^(relleno|plantilla de (arena|material)|acostillado).*(pison de mano)", "relleno_manual"),
    (None, None, r"^(relleno|plantilla de (arena|material)|acostillado|formacion y compact)", "relleno_equipo"),
    (None, None, r"^mejoramiento", "mejoramiento"),
    (None, None, r"^(acarreo|elevacion).*(carretilla|bote|costal)", "acarreo_manual"),
    (None, None, r"^elevacion", "elevacion"),
    (None, None, r"^carga a mano", "carga_mano"),
    (None, None, r"^(acarreo|carga a maquina|apile)", "acarreo_camion"),
    (None, None, r"^ducto .*descenso", "tubo_concreto"),
    (None, None, r"^bombeo", "bombeo"),
    (None, r"base y sub-base", None, "base"),
    (None, None, r"^(riego de|areneado)", "riego_asfalto"),
    (None, None, r"^carpeta", "carpeta"),
    (None, None, r"^(tendido de pavimento|suministro de concreto|calafateo)", "pavimento_concreto"),
    (None, None, r"^(banqueta|guarnicion)", "banqueta"),
    (None, None, r"^atraque", "atraque"),
    (None, None, r"^(brocal|pozo de visita)", "pozo"),
    (None, None, r"^prueba hidrostatica", "prueba"),
    (None, None, r"^plantilla", "plantilla"),
    (None, None, r"^(concreto|mezcla|mortero)[^,]*(hecho en obra|proporcion|yeso)[^,]*$", "mezcla"),
    (None, None, r"^(mezcla|mortero)\b", "mezcla"),
    (None, None, r"^concreto", "concreto"),
    (None, None, r"^acero de refuerzo", "acero"),
    (None, None, r"^malla electrosoldada", "malla"),
    (None, None, r"^cimbra", "cimbra"),
    (None, None, r"^(curado|polietileno)", "curado"),
    (None, None, r"^pulido", "pulido"),
    (None, None, r"^cimiento de piedra", "cimiento_piedra"),
    (None, None, r"^pepena", "pepena"),
    (None, None, r"^(cimiento de concreto|zapata)", "cimiento_concreto"),
    (None, None, r"muro de contencion", "muro_contencion"),
    (None, None, r"^(columna|trabe|contra?t?rabe)\b.*concreto", "elemento_concreto"),
    (None, None, r"^losa.*(vigueta|panel)", "losa_vigueta"),
    (None, None, r"^losa", "losa"),
    (None, None, r"^asentamiento de placas", "grout"),
    (r"estructura", r"estructura metalica", None, "est_metalica"),
    (r"estructura", r"cubiertas de lamina", None, "cubierta_lamina"),
    (None, None, r"^muro.*(tabique|tabicon|ladrillo)", "muro_tabique"),
    (None, None, r"^muro.*covintec", "muro_covintec"),
    (None, None, r"^muro.*(block|tepetate)", "muro_block"),
    (None, None, r"^muro.*piedra", "muro_piedra"),
    (None, None, r"^(cadena|dala|castillo)", "cadena"),
    (None, None, r"^(aplanado|boquilla|fino de aplanado)", "aplanado"),
    (None, None, r"^(firme|piso de \d+ ?cm)", "firme"),
    (None, None, r"^registro", "registro"),
    (None, None, r"^tubo de .*concreto", "tubo_concreto"),
    (None, None, r"^cama de arena", "cama_arena"),
    (None, None, r"^escalon", "escalon"),
    (None, None, r"^(entortado|enladrillado|chaflan|sardinel)", "azotea"),
    (None, None, r"^lavadero", "lavadero"),
    (None, None, r"^impermeabiliza", "imper"),
    (r"muros y plafones", None, r"modular", "plafon_modular"),
    (r"muros y plafones", None, r"plafon", "plafon_panel"),
    (r"muros y plafones", None, None, "muro_panel"),
    (None, None, r"^(zoclo|nariz)", "zoclo"),
    (None, r"losetas", None, "loseta_vinilica"),
    (None, None, r"^mosaico", "mosaico"),
    (None, r"pisos y azulejos", None, "ceramico"),
    (None, r"marmol|barro y cantera", None, "piedra_natural"),
    (None, r"pinturas", r"^pintura|^esmalte|^barniz|^sellador|^impermeabilizante", "pintura"),
    (None, r"pinturas", None, "pasta"),
    (None, r"alfombra", None, "alfombra"),
    (None, None, r"^domo", "domo"),
    (r"herreria", None, None, "herreria"),
    (r"aluminio", None, r"^celosia|^cristal|^espejo|^pelicula", "aluminio"),
    (r"aluminio", None, None, "aluminio"),
    (None, None, r"^celosia", "aluminio"),
    (r"carpinteria", None, None, "carpinteria"),
    (None, None, r"mampara", "mampara"),
    (None, None, r"^(porta|jabonera|toallero|gancho|barra de seguridad|dispensador|secador|cesto|basurero|cenicero|asiento|accesorios|espejo)", "accesorio"),
    (None, r"llaves y accesorios", None, "accesorio"),
    (r"muebles de bano", None, None, "mueble_sanitario"),
    (None, None, r"^valvula", "valvula"),
    (None, r"coladeras", None, "coladera"),
    (None, r"salidas hidrosanitarias", None, "salida"),
    (None, r"soporteria", None, "soporte"),
    (r"hidrosanitarias|contra incendio|agua potable", None, r"^(tubo|tuberia|tuboplus)", "tuberia"),
    (r"hidrosanitarias|contra incendio|agua potable", None, None, "conexion"),
    (None, r"cables", None, "cable"),
    (None, r"centro de carga|tableros", None, "tablero"),
    (None, r"salidas electricas", None, "salida_electrica"),
    (r"electrica", None, None, "conduit"),
    (None, r"rejillas|compuertas", None, "difusor"),
    (None, r"aislamiento", None, "aislamiento"),
    (None, r"^equipos$", None, "equipo_hvac"),
    (r"aire acondicionado", None, None, "ducto"),
    (r"limpiezas", None, None, "limpieza"),
    (r"jardineria", None, None, "jardineria"),
]
REGLAS = [
    (re.compile(c) if c else None, re.compile(s) if s else None,
     re.compile(d) if d else None, fam)
    for c, s, d, fam in _R
]

_PULG = re.compile(r"(\d+(?:\s+\d+/\d+)?|\d+/\d+)\s*(?:\"|''|pulg|”)")
_MM = re.compile(r"(\d+(?:\.\d+)?)\s*mm")
_CM_DIAM = re.compile(r"(?:de|a) (\d+) a (\d+) cm de diametro|(\d+) cm de diametro")
_TON = re.compile(r"de (\d+(?:\.\d+)?) ton")
_CAL = re.compile(r"cal\.?\s*(\d+/0|\d+)|(\d+)\s*kcm")


def _pulgadas(txt):
    n = 0.0
    for parte in txt.split():
        if "/" in parte:
            a, b = parte.split("/")
            n += float(a) / float(b)
        else:
            n += float(parte)
    return n


def _es_grande(familia, unidad, d):
    """Decide si el concepto usa la variante de rendimiento para tamaño grande."""
    if familia in ("tuberia", "conexion", "valvula", "conduit"):
        limite = 27 if familia == "conduit" else 38
        m = _MM.search(d)
        if m:
            return float(m.group(1)) > limite
        m = _PULG.search(d)
        return bool(m) and _pulgadas(m.group(1)) * 25.4 > limite
    if familia == "ducto":
        m = _PULG.search(d)
        return bool(m) and _pulgadas(m.group(1)) > (16 if unidad == "M" else 24)
    if familia == "cable":
        m = _CAL.search(d)
        if not m:
            return False
        if m.group(2) or "/0" in (m.group(1) or ""):
            return True
        return int(m.group(1)) <= 6
    if familia == "tala":
        m = _CM_DIAM.search(d)
        if not m:
            return False
        return int(m.group(2) or m.group(3) or 0) > 20
    if familia == "equipo_hvac":
        m = _TON.search(d)
        return bool(m) and float(m.group(1)) > 5
    if familia == "tablero":
        return bool(re.search(r"^(centro de carga|tablero)", d))
    if familia == "concreto":
        return "premezclado" in d or "bombeado" in d
    if familia == "cimbra":
        return "aparente" in d
    if familia == "aplanado":
        return "plafon" in d
    if familia == "muro_panel":
        return bool(re.search(r"^muro (doble|curvo)|^murete", d))
    if familia == "herreria":
        return bool(re.search(r"^(escalera|porton)", d))
    if familia == "aluminio":
        return bool(re.search(r"^(puerta|porton|cancel de [3-9]|cancel interior)", d))
    if familia == "carpinteria":
        return bool(re.search(r"^(closet|mueble|despensa|cocina|vestidor|repiza)", d))
    if familia == "mueble_sanitario":
        return bool(re.search(r"^(tina\b|tinaco|cisterna|hidroneumatico|fosa|bomba|motobomba|rotobomba|calentador de paso|biodigestor)", d))
    if familia == "desmontaje":
        return bool(re.search(r"tanque|equipo|subestacion|transformador|elevador|caldera|tablero|poste", d))
    return False


def asignar(concepto):
    """Devuelve (clave_actividad, descripción, cuadrilla, rendimiento) o Nones."""
    c = normalizar(concepto["capitulo"])
    s = normalizar(concepto["subcapitulo"])
    d = normalizar(concepto["descripcion"])
    u = concepto["unidad"]
    for rc, rs, rd, fam in REGLAS:
        if rc and not rc.search(c):
            continue
        if rs and not rs.search(s):
            continue
        if rd and not rd.search(d):
            continue
        tam = "g" if _es_grande(fam, u, d.split("incluye")[0]) else ""
        for clave in ((fam, u, tam), (fam, u, "")):
            if clave in ACTIVIDADES:
                desc, cuad, rend = ACTIVIDADES[clave]
                return "-".join(p for p in clave if p), desc, cuad, rend
        return None, f"Familia '{fam}' sin rendimiento para unidad {u}", None, None
    return None, "Sin regla de rendimiento", None, None
