"""Reglas para asignar a cada concepto de Construbase una clave GuBIMclass.

Cada regla es (capítulo, subcapítulo, descripción, clave, confianza). Los tres
primeros son expresiones regulares sobre texto en minúsculas y sin acentos;
None significa "cualquiera". Se aplica la primera regla que coincida, así que
las reglas específicas van antes que las generales.

Confianza:
  alta  - el concepto identifica claramente el elemento GuBIM.
  media - la clave se deduce del contexto; puede variar según el proyecto
          (p. ej. un muro puede ser tabique interior o fachada).
  baja  - clave genérica del capítulo; conviene revisarla.
"""
import re
import unicodedata


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", str(texto or ""))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.lower()


# Conceptos que son insumos o básicos (mezclas, concretos hechos en obra sin
# colocación): se usan dentro de otros precios y no se modelan en BIM.
BASICO = re.compile(r"^(concreto|mezcla|mortero)\b[^,]*(hecho en obra|proporcion|yeso)", re.I)

R = [
    # --- 00 / 10 / 80: preliminares, terreno, obra temporal -----------------
    (None, None, r"^trazo|nivelacion (de terreno|para|banquetas)", "10.20.10", "alta"),
    (None, None, r"^tapial", "80.10.40.10", "alta"),
    (None, None, r"sanitario portatil", "80.10.30.20", "alta"),
    (None, None, r"^(limpia|desyerbe|desmonte|despalme)", "10.20.20.10", "media"),
    (None, None, r"^tala de arbol", "70.50.10.10", "media"),
    (None, r"desmontajes", None, "00.20", "media"),
    (None, r"demoliciones", None, "00.20", "media"),
    (None, None, r"^(acarreo|carga a (maquina|mano)|apile)", "80.10.70.30", "media"),
    (None, None, r"^ducto .*descenso de materiales", "80.10.70.60", "alta"),
    (None, None, r"^elevacion de materiales", "80.10.20.40", "media"),
    (None, None, r"^bombeo de achique", "10.30.20.10", "alta"),
    (None, None, r"^excavacion.*(cepa|zanja)", "10.20.20.20", "alta"),
    (None, None, r"^(excavacion|corte de terreno)", "10.20.20.10", "alta"),
    (None, None, r"^(afine|pepena)", "10.20.20.20", "media"),
    (None, None, r"^mejoramiento", "10.20.30.20", "alta"),
    (None, None, r"^(formacion y compactacion de terraplen|formacion y compactacon de terraplen)", "10.20.30.10", "alta"),
    (None, r"base y sub-base", None, "70.30.10", "alta"),
    (None, None, r"^relleno .*tezontle en azotea", "30.20.10.10", "media"),  # relleno de pendientes forma parte de la cubierta
    (None, None, r"^(relleno|acostillado|plantilla de (arena|material))", "10.20.30.10", "alta"),

    # --- 20: cimentación y estructura ---------------------------------------
    (None, None, r"^plantilla .*concreto", "20.10.10.50", "alta"),
    (None, None, r"muro de contencion", "20.10.30.10", "alta"),
    (None, None, r"^zapata|cimbra en (zapatas|dados)", "20.10.10.20", "alta"),
    (None, None, r"^cimiento", "20.10.10.20", "alta"),
    (None, None, r"^contra?t?rabe|cimbra en (contratrabes|trabes de cimentacion)", "20.10.10.10", "alta"),
    (None, None, r"losas? de cimentacion", "20.10.10.40", "alta"),
    (None, None, r"rampas? de cimentacion", "20.10.40.20", "alta"),
    (None, None, r"muros de cimentacion", "20.10.30.10", "media"),
    (None, None, r"columnas de cimentacion", "20.20.10.10", "media"),
    (None, None, r"^atraque", "70.40.30.10", "media"),
    (r"^cimentacion", None, None, "20.10.10", "baja"),

    (None, None, r"^(cimbra en )?(columna|castillo)s?\b.*sonotubo", "20.20.10.10", "alta"),
    (r"estructura", None, r"columna", "20.20.10.10", "alta"),
    (r"estructura", None, r"cimbra en muros", "20.20.10.30", "alta"),
    (r"estructura", None, r"rampa", "20.20.10.50", "alta"),
    (r"estructura", None, r"^losa|losas|vigueta|panel w", "20.20.20.10", "alta"),
    (r"estructura", None, r"^trabe|trabes|vigas|ipr", "20.20.20.20", "alta"),
    (r"estructura", None, r"armadura", "20.20.20.30", "alta"),
    (r"estructura", None, r"placa|asentamiento de placas", "20.20.10.10", "media"),
    (r"estructura", r"cubiertas de lamina", r"multymuro|en muros", "30.10.10.20", "alta"),
    (r"estructura", r"cubiertas de lamina", r"turbo|extractor|ventila", "50.30.10.80", "alta"),
    (r"estructura", r"cubiertas de lamina", r"traslucid|tragaluz|domo", "30.20.20.10", "media"),
    (r"estructura", r"cubiertas de lamina", r"^(canalon|caballete|casquillo|gotero|remate)", "30.20.10.50", "alta"),
    (r"estructura", r"cubiertas de lamina", None, "30.20.10.20", "alta"),
    (r"estructura", r"estructura metalica", None, "20.20.20.20", "media"),
    (r"estructura", None, None, "20.20", "baja"),

    # --- albañilería ----------------------------------------------------------
    (None, r"castillos", None, "20.20.10.10", "media"),
    (None, r"cadenas y dalas|^dalas", r"desplante", "20.10.10.10", "media"),
    (None, r"cadenas y dalas|^dalas", None, "20.20.20.20", "media"),
    (None, r"^muros$", r"piedra braza", "20.10.30.10", "media"),
    (None, r"^muros$", None, "40.10.10.10", "media"),
    (None, r"aplanados", r"plafon", "40.20.20.10", "alta"),
    (None, r"aplanados", r"exterior|fachada", "30.10.10.40", "alta"),
    (None, r"aplanados", None, "40.10.20.20", "media"),
    (None, r"pisos y firmes", r"rampa", "20.10.40.20", "alta"),
    (None, r"pisos y firmes", r"^firme", "40.20.10.30", "alta"),  # firme = recrecido (decisión Carlos, 2026-09-25)
    (None, r"pisos y firmes", None, "40.20.20.20", "media"),
    (None, None, r"^registro electrico", "50.60.30.50", "alta"),
    (None, None, r"^(registro|brocal|pozo de visita)", "50.20.20.50", "alta"),
    (None, r"registros y tuberia", None, "50.20.20.20", "media"),
    (None, None, r"^escalon", "40.30.10.10", "media"),
    (None, None, r"^(sardinel|chaflan)", "30.20.10.50", "media"),
    (None, r"varios", r"azotea|^entortado|^enladrillado", "30.20.10.10", "alta"),
    (None, None, r"^lavadero", "60.10.10.90", "alta"),
    (None, None, r"^celosia", "30.10.20.30", "alta"),
    (None, r"impermeabilizacion", r"desplante", "20.10.10.10", "media"),
    (None, r"impermeabilizacion", None, "30.20.10.40", "alta"),
    (None, r"basicos", None, None, "insumo"),

    # --- muros y plafones de panel -------------------------------------------
    (r"muros y plafones", None, r"^columna", "40.10.10.30", "media"),
    (r"muros y plafones", None, r"plafon|plafond|cajillo|platabanda", "40.20.10.10", "alta"),
    (r"muros y plafones", None, r"exterior", "30.10.10.10", "media"),
    (r"muros y plafones", None, r"compuesto por 1 panel\b", "40.10.10.30", "media"),  # forro de una cara (CDMX: lambrín)
    (r"muros y plafones", None, None, "40.10.10.10", "alta"),

    # --- acabados -------------------------------------------------------------
    (r"acabados", None, r"^teja", "30.20.10.40", "alta"),
    (r"acabados", None, r"^cubierta de|cubiertas|ovalin|lavabo|mesa|barra", "60.20.10.10", "media"),
    (r"acabados", None, r"zoclo", "40.10.20.30", "alta"),
    (r"acabados", None, r"escalon|huella|peralte|escalera", "40.30.20.10", "alta"),
    (r"acabados", None, r"^muro de", "40.10.10.10", "media"),
    (r"acabados", None, r"fachada|exterior", "30.10.10.40", "media"),
    (r"acabados", r"pinturas", r"trafico", "40.40.10.30", "media"),
    (r"acabados", r"pinturas", r"plafon", "40.20.20.10", "alta"),
    (r"acabados", r"pinturas", None, "40.10.20.40", "alta"),
    (r"acabados", None, r"en muros|muro|\bazulejo|lambrin|recubrimiento", "40.10.20.10", "media"),
    (r"acabados", None, None, "40.20.20.20", "media"),

    # --- herrería, aluminio, carpintería -------------------------------------
    (None, None, r"^escalera", "20.20.10.40", "media"),
    (None, None, r"^tapa (para cisterna|de .*rejilla)|^rejilla irving", "50.20.20.50", "media"),
    (None, None, r"^alambre de puas", "70.20.10", "alta"),
    (None, None, r"barandal|pasamanos", "40.10.10.50", "alta"),
    (None, None, r"^(cerca|concertina|malla ciclonica|reja perimetral)", "70.20.10", "alta"),
    (None, None, r"^porton", "70.20.10", "media"),
    (None, None, r"^domo", "30.20.20.10", "alta"),
    (None, None, r"^espejo", "60.20.10.30", "alta"),
    (None, None, r"cancel (para|de) bano", "40.10.10.20", "alta"),
    (None, None, r"cancel interior", "40.10.10.20", "alta"),
    (r"herreria", None, r"^puerta", "30.10.20.20", "media"),
    (r"herreria", None, r"ventana", "30.10.20.10", "media"),
    (r"herreria", None, r"proteccion|reja", "30.10.20.40", "alta"),
    (r"herreria", None, None, "30.10.20.40", "baja"),
    (r"aluminio", None, r"^puerta|batiente", "30.10.20.20", "media"),
    (r"aluminio", None, None, "30.10.20.10", "media"),
    (r"carpinteria", None, r"closet|vestidor", "60.20.10.60", "alta"),
    (r"carpinteria", None, r"^puerta", "40.10.10.40", "alta"),
    (r"carpinteria", None, r"^zoclo", "40.10.20.30", "alta"),
    (r"carpinteria", None, r"lambrin", "40.10.20.10", "alta"),
    (r"carpinteria", None, r"^piso|duela|parquet", "40.20.20.20", "alta"),
    (r"carpinteria", None, r"repisa|entrepano|estante", "60.20.10.20", "alta"),
    (r"carpinteria", None, None, "60.20.10.50", "media"),

    # --- muebles de baño, cocinas ---------------------------------------------
    (None, None, r"mampara", "40.10.10.20", "alta"),
    (None, None, r"^(inodoro|w\.?c\.?|taza)", "60.10.10.10", "alta"),
    (None, None, r"^mingitorio|^urinario", "60.10.10.20", "alta"),
    (None, None, r"^bide", "60.10.10.30", "alta"),
    (None, None, r"^(lavabo|ovalin)", "60.10.10.60", "alta"),
    (None, None, r"^(tina\b|jacuzzi|hidromasaje)", "60.10.10.50", "alta"),
    (None, None, r"^(plato|receptaculo) de ducha|^receptaculo", "60.10.10.40", "alta"),
    (None, None, r"^(tarja|fregadero)", "60.10.10.70", "alta"),
    (None, None, r"^(tinaco|cisterna|deposito|calentador|boiler|termotanque)", "50.10.10.30", "alta"),
    (None, None, r"^(bomba|motobomba|rotobomba|hidroneumatico|equipo de bombeo)", "50.10.10.20", "alta"),
    (None, None, r"^(fosa|fosaplas|biodigestor)", "50.20.10.30", "alta"),
    (None, None, r"^(campana|parrilla|estufa|horno)", "60.10.20.60", "alta"),
    (None, r"cocinas", r"cocina integral|gabinete|alacena", "60.20.10.50", "alta"),
    (None, None, r"^(porta|jabonera|toallero|gancho|barra de seguridad|dispensador|secador|cesto|basurero|cenicero|asiento|accesorios de bano)", "60.10.10.80", "alta"),
    (None, None, r"^juego de muebles de bano", "60.10.10", "media"),
    (None, r"llaves y accesorios", None, "50.10.20.60", "alta"),
    (r"muebles de bano", None, None, "60.10.10.80", "baja"),

    # --- instalaciones hidrosanitarias ---------------------------------------
    (r"hidrosanitarias", None, r"^valvula|^llave de (paso|nariz)", "50.10.20.10", "alta"),
    (r"hidrosanitarias", r"coladeras", r"fluxometro", "50.10.20.60", "alta"),
    (r"hidrosanitarias", r"coladeras", None, "50.20.20.60", "alta"),
    (r"hidrosanitarias", r"salidas", r"sanitaria para|desague|drenaje", "50.20.20.20", "media"),
    (r"hidrosanitarias", r"salidas", None, "50.10.20.30", "media"),
    (r"hidrosanitarias", r"pvc sanitario|fo\.?fo", r"ventila", "50.20.20.40", "media"),
    (r"hidrosanitarias", r"pvc sanitario|fo\.?fo", r"pluvial", "50.20.20.10", "alta"),
    (r"hidrosanitarias", r"pvc sanitario|fo\.?fo", None, "50.20.20.20", "alta"),
    (r"hidrosanitarias", r"fierro negro", None, "50.40.30.10", "media"),
    (r"hidrosanitarias", r"valvulas", None, "50.10.20.10", "alta"),
    (r"hidrosanitarias", None, None, "50.10.20.30", "alta"),
    (r"agua potable", None, r"^valvula", "50.10.20.10", "alta"),
    (r"agua potable", None, None, "50.10.20.30", "media"),
    (r"drenaje", None, None, "70.40.30.10", "media"),

    # --- instalación eléctrica ----------------------------------------------
    (r"electrica", r"cables", None, "50.60.30.60", "alta"),
    (r"electrica", r"centro de carga|tableros", None, "50.60.10.10", "alta"),
    (r"electrica", r"condulet", None, "50.60.30.30", "alta"),
    (r"electrica", r"ducto cuadrado", None, "50.60.30.20", "alta"),
    (r"electrica", r"salidas", r"contacto", "50.60.40.20", "alta"),
    (r"electrica", r"salidas", None, "50.60.40.10", "media"),
    (r"electrica", None, r"^caja", "50.60.30.30", "alta"),
    (r"electrica", None, None, "50.60.30.40", "alta"),

    # --- aire acondicionado ---------------------------------------------------
    (r"aire acondicionado", None, r"^rejilla", "50.30.50.50", "alta"),
    (r"aire acondicionado", None, r"^difusor|difusor", "50.30.50.20", "alta"),
    (r"aire acondicionado", None, r"^compuerta", "50.30.20.30", "alta"),
    (r"aire acondicionado", r"aislamiento", None, "50.30.30.20", "media"),
    (r"aire acondicionado", r"equipos", r"extractor|ventilador", "50.30.10.80", "alta"),
    (r"aire acondicionado", r"equipos", r"fan ?coil|manejadora|evaporador|unidad interior|cassette|ventilador serpentin", "50.30.10.30", "alta"),
    (r"aire acondicionado", r"equipos", None, "50.30.10.20", "media"),
    (r"aire acondicionado", None, r"extraccion", "50.30.40.20", "media"),
    (r"aire acondicionado", None, None, "50.30.40.30", "media"),

    # --- contra incendio ------------------------------------------------------
    (r"contra incendio", r"soporteria", None, "50.100.10.10", "alta"),
    (r"contra incendio", None, r"^valvula", "50.50.10.30", "alta"),
    (r"contra incendio", None, r"rociador", "50.50.10.60", "alta"),
    (r"contra incendio", None, r"gabinete|hidrante", "50.50.10.70", "alta"),
    (r"contra incendio", None, r"extintor", "50.50.10.80", "alta"),
    (r"contra incendio", None, None, "50.50.10.50", "alta"),

    # --- limpiezas, jardinería, urbanización ---------------------------------
    (r"limpiezas", None, None, "80.10.70", "baja"),
    (r"jardineria", None, r"arbol", "70.50.10.10", "alta"),
    (r"jardineria", None, r"pasto|cesped", "70.50.10.20", "alta"),
    (r"jardineria", None, r"tierra vegetal", "70.50.20.10", "media"),
    (r"jardineria", None, None, "70.50.10.30", "alta"),
    (r"pavimentos", r"banquetas", r"guarnicion|banqueta", "70.30.20", "alta"),
    (r"pavimentos", None, None, "70.30.30", "alta"),
    (r"terracerias", None, None, "10.20", "baja"),
]

REGLAS = [
    (re.compile(c) if c else None, re.compile(s) if s else None,
     re.compile(d) if d else None, codigo, conf)
    for c, s, d, codigo, conf in R
]


def clasificar(concepto):
    """Devuelve (clave_gubim, confianza) para un concepto de leer_construbase."""
    desc = concepto["descripcion"]
    if BASICO.search(desc) and desc.upper() == desc:
        return None, "insumo"
    c = normalizar(concepto["capitulo"])
    s = normalizar(concepto["subcapitulo"])
    d = normalizar(desc)
    for rc, rs, rd, codigo, conf in REGLAS:
        if rc and not rc.search(c):
            continue
        if rs and not rs.search(s):
            continue
        if rd and not rd.search(d):
            continue
        return codigo, conf
    return None, "sin regla"
