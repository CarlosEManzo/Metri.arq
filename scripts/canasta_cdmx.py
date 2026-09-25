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
    # Parte 2: cimbras de cimentación y castillo aparente (pares verificados en el tabulador)
    ("E02.01.0120", "CB12BD", 1, "exacta", "Cimbra común en contratrabes de cimentación"),
    ("E02.01.0121", "CB12BD", 1, "exacta", "Cimbra común en dados de cimentación"),
    ("E02.01.0123", "CB12BG", 1, "aproximada", "Cimbra común en columnas (CDMX columnas hasta 4 m)"),
    ("E02.01.0124", "CB12BL", 1, "aproximada", "Cimbra común en trabes (CDMX trabes aisladas hasta 4 m)"),
    ("E02.01.0129", "CC14BG", 1, "aproximada", "Cimbra aparente en columnas (CDMX columnas hasta 4 m)"),
    ("E02.01.0130", "CC14BL", 1, "aproximada", "Cimbra aparente en trabes (CDMX trabes aisladas hasta 4 m)"),
    ("E02.01.0131", "CC14BH", 1, "exacta", "Cimbra aparente en muros"),
    ("E02.01.0132", "CC14BJ", 1, "aproximada", "Cimbra aparente en losas (CDMX losas y trabes)"),
    ("E04.04.0009", "GC31JC", 1, "aproximada", "Castillo 15x15 aparente (armex contra 4 varillas 3/8\", CDMX acabado común)"),

    # Parte 3: muros y plafones, básicos, acabados, domos y cristales (pares verificados en el tabulador)
    ("E05.01.0002", "GC29IB", 1, "exacta", "Muro tablaroca 2 caras 6.7 cm"),
    ("E05.01.0009", "GC29IC", 1, "exacta", "Muro tablaroca 2 caras 8.9 cm"),
    ("I05.01.0001", "GC29IC", 1, "exacta", "Muro tablaroca 2 caras 8.9 cm (Intelimat)"),
    ("E05.01.0008", "LB16AD", 1, "exacta", "Muro de 1 panel 7.6 cm (CDMX lambrín)"),
    ("E05.01.0015", "LB16AE", 1, "exacta", "Muro de 1 panel 10.5 cm (CDMX lambrín)"),
    ("E05.02.0002", "GC29FC", 1, "exacta", "Muro resistente al fuego 2 caras 8.9 cm"),
    ("E05.03.0002", "GC29HC", 1, "exacta", "Muro resistente a la humedad 2 caras 8.9 cm"),
    ("E05.04.0001", "LB16AB", 1, "exacta", "Durock 1 cara 7.6 cm (CDMX lambrín)"),
    ("E05.04.0002", "GC29GB", 1, "aproximada", "Durock 2 caras (CDMX canal C-22)"),
    ("E05.05.0002", "GE12BB", 1, "exacta", "Plafón resistente al fuego 13 mm"),
    ("E05.05.0003", "GE12IB", 1, "exacta", "Plafón resistente a la humedad 13 mm"),
    ("E05.05.0005", "GE12JB", 1, "aproximada", "Plafón Durock (CDMX canal listón C-20)"),
    ("E05.07.0001", "GE12HB", 1, "aproximada", "Plafón modular 61x61 (Cortega contra Smart Futura)"),
    ("E04.01.0006", "F2*C02", 1, "exacta", "Básico cemento-cal-arena 1:1:6 (a costo directo)"),
    ("E04.01.0007", "F2*C04", 1, "exacta", "Básico cemento-cal-arena 1:1:8 (a costo directo)"),
    ("E04.01.0003", "F2*C10", 1, "aproximada", "Básico cemento-cal-arena 1:0.25:3 contra 1:0.25:4 (a costo directo)"),
    ("E04.01.0004", "F5*1B1", 1, "aproximada", "Básico concreto f'c 150, TMA 9 contra 19 mm (a costo directo)"),
    ("E04.01.0005", "F5*1D1", 1, "aproximada", "Básico concreto f'c 200, TMA 9 contra 19 mm (a costo directo)"),
    ("E06.01.0002", "GH22BB", 1, "exacta", "Loseta vinílica 30x30 1.6 mm"),
    ("E06.01.0004", "GH22BB", 1, "aproximada", "Loseta vinílica 30x30 1.6 mm (otro modelo)"),
    ("E06.01.0009", "GH22BB", 1, "aproximada", "Loseta vinílica 30x30 1.6 mm (otro modelo)"),
    ("E06.01.0012", "GH22BB", 1, "aproximada", "Loseta vinílica 30x30 1.6 mm (otro modelo)"),
    ("E06.01.0013", "GH22BB", 1, "aproximada", "Loseta vinílica 30x30 1.6 mm (otro modelo)"),
    ("E06.01.0018", "GH22BB", 1, "aproximada", "Loseta vinílica 30x30 1.6 mm (otro modelo)"),
    ("E06.01.0019", "GH22BB", 1, "aproximada", "Loseta vinílica 30x30 1.6 mm (otro modelo)"),
    ("E06.01.0003", "GH22BC", 1, "aproximada", "Loseta vinílica 30x30 3.1 mm contra 3 mm"),
    ("E06.01.0005", "GH22BC", 1, "aproximada", "Loseta vinílica 30x30 3.1 mm contra 3 mm"),
    ("E06.01.0006", "GH22BC", 1, "aproximada", "Loseta vinílica 30x30 3.1 mm contra 3 mm"),
    ("E06.01.0007", "GH22BC", 1, "aproximada", "Loseta vinílica 30x30 3.1 mm contra 3 mm"),
    ("E06.01.0016", "GH22BC", 1, "aproximada", "Loseta vinílica 30x30 3.1 mm contra 3 mm"),
    ("E06.01.0022", "GI12CB", 1, "exacta", "Zoclo vinílico 7 cm"),
    ("E06.01.0023", "GI12CF", 1, "exacta", "Zoclo vinílico 10 cm"),
    ("E06.04.0005", "GH20EB", 1, "aproximada", "Adocreto negro 6 cm (cuadrado contra cruz)"),
    ("E06.04.0007", "QM12BJ", 1, "exacta", "Adocreto hexagonal 8 cm"),
    ("E06.04.0009", "QM12BL", 1, "exacta", "Adocreto tipo I 8 cm"),
    ("I06.01.0002", "GH16HD", 1, "aproximada", "Piso Porcelanite 33x33 (otro modelo)"),
    ("I06.01.0004", "GH16GB", 1, "aproximada", "Piso 30x30 (Lamosa contra Porcelanite)"),
    ("I06.01.0001", "LB16FB", 1, "aproximada", "Muro Andes 20x30 (CDMX sin listel)"),
    ("E06.06.0036", "GH24BB", 1, "aproximada", "Alfombra Sprint con bajo alfombra"),
    ("E06.05.0007", "LG13BI", 1, "aproximada", "Esmalte 100 en muros"),
    ("E06.05.0008", "LG13BI", 1, "aproximada", "Esmalte 100 en plafones"),
    ("E08.08.0021", "GM13BB", 1, "aproximada", "Domo acrílico con ventila 60x60"),
    ("E08.08.0023", "GM13BC", 1, "aproximada", "Domo acrílico con ventila 90x90"),
    ("E08.08.0037", "GM13BD", 1, "aproximada", "Domo acrílico con ventila 90x120"),
    ("E08.08.0041", "GM13BE", 1, "aproximada", "Domo acrílico con ventila 90x180"),
    ("E08.08.0043", "GM13BF", 1, "aproximada", "Domo acrílico con ventila 90x240"),
    ("E08.08.0001", "MB13BE", 1, "aproximada", "Cristal flotado claro 6 mm (CDMX medidas máximas)"),
    ("E08.08.0007", "MB13CJ", 1, "aproximada", "Cristal flotado bronce 6 mm (CDMX medidas máximas)"),
]
