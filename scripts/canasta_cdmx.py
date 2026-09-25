"""Canasta curada: conceptos típicos de vivienda emparejados a mano con el
Tabulador General de Precios Unitarios de la CDMX (actualización julio 2026).

El emparejamiento automático solo es confiable en instalaciones, donde las
descripciones son casi iguales. Para el resto de la obra (terracerías,
cimentación, albañilería, acabados) cada par se eligió leyendo ambos
catálogos. Cada renglón: clave Construbase, clave CDMX, factor para llevar el
P.U. de la CDMX a la unidad de Construbase, equivalencia y nota.

    exacta      mismo trabajo y mismas medidas
    aproximada  mismo trabajo con alguna diferencia (modelo, espesor, sistema)
"""

CANASTA = [
    # Preliminares, terracerías y acarreos
    ("E01.01.0002", "AF13DB", 1, "exacta", "Trazo y nivelación con equipo topográfico"),
    ("E01.04.0032", "BL12FB", 0.14, "aproximada", "Demolición muro de tabique 14 cm; CDMX por m3 → m2 (× 0.14)"),
    ("E02.01.0027", "BF13BB", 1, "exacta", "Excavación a mano 0–2 m, material tipo I"),
    ("E02.01.0019", "BG12BB", 1, "exacta", "Excavación a máquina 0–2 m, material tipo I"),
    ("E02.01.0137", "BP12BB", 1, "exacta", "Relleno con material producto de excavación, pisón de mano"),
    ("E02.01.0039", "BN16BB", 1, "exacta", "Carga mecánica y acarreo en camión 1er km"),
    ("E02.01.0040", "BN15BB", 1, "exacta", "Carga manual y acarreo en camión 1er km"),
    # Cimentación, concreto, acero y cimbra
    ("E02.01.0087", "GG13BB", 1, "exacta", "Plantilla de concreto f'c=100 de 5 cm"),
    ("E02.01.0122", "CB12BD", 1, "exacta", "Cimbra común en zapatas de cimentación"),
    ("E02.01.0066", "DB12CC", 0.001, "exacta", "Acero de refuerzo #3 Fy 4200; CDMX por ton → kg"),
    ("E03.01.0007", "DB12CD", 0.001, "exacta", "Acero de refuerzo #4 Fy 4200; CDMX por ton → kg"),
    ("E02.01.0079", "DB15BG", 1, "exacta", "Malla electrosoldada 6x6-10/10"),
    ("E02.01.0098", "FC15CB", 1, "exacta", "Concreto f'c=250 hecho en obra, en cimentación"),
    ("E03.01.0064", "FJ18BC", 1, "exacta", "Concreto premezclado estructural f'c=250 bombeado"),
    ("E03.01.0026", "CB12BJ", 1, "exacta", "Cimbra común en losas"),
    ("E03.01.0025", "CB12BL", 1, "exacta", "Cimbra común en trabes"),
    # Albañilería
    ("E04.02.0002", "GC16BB", 1, "exacta", "Muro de tabique rojo recocido 14 cm, acabado común"),
    ("E04.02.0033", "GC23CN", 1, "exacta", "Muro de block de concreto 15x20x40 con escalerilla"),
    ("E04.04.0008", "GC31JC", 1, "aproximada", "Castillo 15x15 (armex contra 4 varillas 3/8\")"),
    ("E04.03.0003", "GC31LD", 1, "exacta", "Cadena 15x20 f'c=200, 4 varillas 3/8\""),
    ("E04.05.0003", "LB12CD", 1, "exacta", "Aplanado fino en muros, mortero cemento-arena"),
    ("E04.05.0023", "LB12DD", 1, "aproximada", "Aplanado fino en plafón (mortero con cal en CDMX)"),
    ("E04.06.0014", "GH12BE", 1, "exacta", "Firme de concreto f'c=150 de 10 cm"),
    ("E04.08.0012", "GN12BB", 1, "exacta", "Relleno de tezontle en azotea para pendientes"),
    ("E04.08.0013", "GP12BB", 1, "aproximada", "Entortado en azotea (4 cm contra 3 cm)"),
    ("E04.08.0014", "GO12BB", 1, "exacta", "Enladrillado de azotea"),
    ("E04.07.0002", "HE12CB", 1, "aproximada", "Registro 0.40x0.60 (0.80 contra 0.75 m de profundidad)"),
    ("E04.09.0004", "GS12DD", 1, "aproximada", "Impermeabilización asfáltica prefabricada en frío con membrana de refuerzo"),
    # Muros y plafones de panel
    ("E05.01.0016", "GC29ID", 1, "exacta", "Muro de panel de yeso estándar 11.8 cm, dos caras"),
    ("E05.05.0001", "GE12KB", 1, "exacta", "Plafón de panel de yeso estándar 13 mm"),
    # Acabados
    ("E06.02.0044", "GH16HD", 1, "exacta", "Piso de loseta Porcelanite 33x33 con adhesivo"),
    ("E06.02.0042", "LB16GB", 1, "aproximada", "Azulejo en muros línea económica contra Vitromex 20x30"),
    ("E06.05.0017", "LG12FC", 1, "exacta", "Pintura vinílica Vinimex en muros"),
    ("E06.05.0010", "LG13BE", 1, "aproximada", "Esmalte en superficies metálicas"),
    # Instalaciones
    ("E11.05.0004", "HB12BE", 1, "exacta", "Tubo de PVC sanitario de 100 mm"),
    ("E11.01.0023", "IB12BD", 1, "exacta", "Tubo de cobre tipo M de 13 mm"),
    ("E12.06.0021", "KC16BF", 1, "exacta", "Cable THW cal. 12 Condumex"),
    ("E12.02.0001", "KG12BD", 1, "exacta", "Tubo conduit PVC pesado de 1/2\""),
    ("E10.02.0017", "HI13BD", 1, "aproximada", "Inodoro American Standard Cadet"),
    # Carpintería y exteriores
    ("E09.02.0008", "CG16DB", 1, "aproximada", "Puerta de tambor 0.90x2.10 de triplay de pino"),
    ("E16.01.0017", "VC12BC", 1, "aproximada", "Pasto en rollo (alfombra contra San Agustín)"),
]
