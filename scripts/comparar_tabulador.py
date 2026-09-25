"""Compara la tabla Construbase -> GuBIM contra el Tabulador General de
Precios Unitarios del Gobierno de la CDMX.

Uso:
    python3 scripts/comparar_tabulador.py fuentes/tabulador_cdmx.pdf

Empareja cada concepto de Construbase con el concepto más parecido del
tabulador (misma unidad, descripción parecida y mismas medidas: espesores,
f'c, diámetros, calibres) y compara el P.U. actualizado con el del tabulador.
El resultado va a salida/comparacion_tabulador.csv y a una hoja nueva del
Excel.

El tabulador de la CDMX publica precios unitarios, no las matrices: sirve
para validar precios (y, en conceptos de mucha mano de obra, para detectar
rendimientos fuera de lugar), no para leer rendimientos directamente.
"""
import collections
import csv
import math
import re
import statistics
import sys
from pathlib import Path

from rapidfuzz import fuzz, process

from reglas_gubim import normalizar

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "salida"
REFERENCIAS = RAIZ / "referencias"

SIMILITUD_ALTA = 85   # pares automáticos que se usan como evidencia
MINIMO_PARES = 10     # pares por familia para sugerir un ajuste
TOLERANCIA = 0.10     # diferencia mínima (±10 %) para sugerir un ajuste

# Notas del Tabulador General de Precios Unitarios CDMX, edición 2026
# (vigencia a partir de marzo 2026), numeral 9:
#   P.U. = costo directo + indirectos + financiamiento + utilidad + cargos adicionales
#   indirecto integrado (indirectos, financiamiento y utilidad) = 27.51 % sobre costo directo
#   cargos adicionales = 3.627 % (derechos de supervisión 1.5 % e inspección 2 % del
#   Código Fiscal de la CDMX; no aplican fuera de la obra pública de la CDMX)
#   sin IVA. Los conceptos "Básicos" (capítulo BAS) están a costo directo (numeral 11).
INDIRECTO_CDMX = 0.2751
CARGOS_ADICIONALES_CDMX = 0.03627
FACTOR_SIN_CARGOS = 1 / (1 - CARGOS_ADICIONALES_CDMX)    # P.U. con cargos / P.U. sin cargos
FACTOR_PU_A_CD = (1 + INDIRECTO_CDMX) * FACTOR_SIN_CARGOS  # P.U. CDMX / costo directo ≈ 1.323

# Capítulos del tabulador (índice general, edición 2026).
CAPITULOS_CDMX = {
    "A": "Anteproyectos, proyectos, estudios, trabajos de campo y laboratorio",
    "B": "Desyerbe, desmonte, tala, despalme, excavaciones, demoliciones, acarreos y rellenos",
    "C": "Cimbra, estructuras de madera y carpintería",
    "D": "Acero de refuerzo para concreto",
    "E": "Estructura metálica, hierro y aluminio",
    "F": "Concreto hidráulico",
    "G": "Cimientos, muros, pisos, techados y enladrillados",
    "H": "Instalaciones sanitarias",
    "I": "Instalaciones hidráulicas",
    "J": "Instalaciones complementarias en edificios",
    "K": "Instalaciones eléctricas en general",
    "L": "Recubrimientos, acabados, pinturas y herrajes",
    "M": "Vidriería",
    "N": "Alcantarillado",
    "O": "Construcción de sistemas de agua potable",
    "Q": "Obras viales",
    "R": "Pilotes y pilas",
    "S": "Banquetas, guarniciones y andaderos",
    "T": "Alumbrado público y trabajos afines",
    "U": "Señalización en vialidades",
    "V": "Áreas ajardinadas y forestación",
    "Z": "Realización de limpieza",
    "BAS": "Básicos (a costo directo)",
    "ATI": "Tabulador atípico (grandes volúmenes)",
    "RM": "Reciclado de materiales",
}


def capitulo_cdmx(clave):
    clave = clave.upper()
    for prefijo in ("BAS", "ATI", "RM"):
        if clave.startswith(prefijo):
            return prefijo
    return clave[:1]


UMBRAL = 70          # similitud mínima (0-100): con 70 se recuperan ~98 % de los pares en la prueba sintética
RANGO_OK = (0.75, 1.33)  # cociente tabulador / actualizado considerado congruente

UNIDADES = {
    "m2.": "M2", "m3.": "M3", "lto": "LOTE", "lto.": "LOTE", "m3-est": "M3/E", "m3-est.": "M3/E",
    "m3-estac": "M3/E", "ton-km": "TON/KM", "pza-km": "PZA/KM", "dia": "DIA", "día": "DIA",
    "semana": "SEMANA", "litro": "LT", "lt": "LT", "p.t.": "PT", "p.t": "PT",
    "m2": "M2", "m²": "M2", "m3": "M3", "m³": "M3", "m": "M", "ml": "M", "pza": "PZA",
    "pieza": "PZA", "kg": "KG", "ton": "TON", "t": "TON", "sal": "SAL", "salida": "SAL",
    "jgo": "JGO", "juego": "JGO", "lote": "LOTE", "ha": "HA", "hr": "HR", "hora": "HR",
    "m3-km": "M3/KM", "m3/km": "M3/KM", "m3km": "M3/KM", "viaje": "VIAJE", "mes": "MES",
}

_NUM = re.compile(r"\d+(?:[.,]\d+)?(?:\s*/\s*\d+)?")
_RUIDO = re.compile(r"\b(incluye|incluyendo)\b.*$")


def nucleo(texto):
    """Parte de la descripción que identifica el concepto (antes de 'incluye')."""
    t = normalizar(texto)
    t = _RUIDO.sub("", t)
    t = re.sub(r"\([^)]*\)", " ", t)   # equivalencias entre paréntesis: 32 mm (1 1/4")
    return re.sub(r"[^a-z0-9/.=]+", " ", t).strip()


def medidas(texto):
    return {m.replace(",", ".").replace(" ", "") for m in _NUM.findall(nucleo(texto))}


def unidad_std(u):
    u = normalizar(u).strip().replace(".", "")
    return UNIDADES.get(u, u.upper())


# --- Lectura del PDF ----------------------------------------------------------
#
# Formato del tabulador (edición 2026): texto, una página por hoja con el
# encabezado "Clave Concepto de Obra Unidad P. U.". Los encabezados de grupo
# no tienen precio (p. ej. "BF13B Excavación a mano ... medido en banco.") y los
# conceptos terminan su primera línea con "unidad precio"; la descripción puede
# continuar en las líneas siguientes. Las secciones BAS (básicos, a costo
# directo), ATI (atípico) y RM (reciclados) van al final del documento.

_CLAVE = re.compile(r"^([A-Z][A-Z0-9*]{0,11})\s+(.+)$")
_CONCEPTO = re.compile(r"^(.*\S)\s+(\S+)\s+(\d{1,3}(?:,\d{3})*\.\d{2})$")
_SECCIONES = {"BAS": "BAS", "ATI": "ATI", "RM": "RM"}
# Pie de página (dirección de la Secretaría), a veces pegado al final de un renglón.
_PIE = re.compile(r"\s*Plaza de la Constituci[oó]n 1.*$")
_PIE_RESTO = re.compile(r"^(de la Ciudad de México, Alcaldía Cuauhtémoc|06000, T\. 55)")


def _es_clave_de_concepto(clave):
    return any(ch.isdigit() for ch in clave)


def leer_tabulador_pdf(ruta):
    """Devuelve [{clave, concepto, grupo, unidad, pu, seccion}] del PDF del tabulador."""
    import pdfplumber

    lineas = []
    with pdfplumber.open(ruta) as pdf:
        for pagina in pdf.pages:
            texto = (pagina.extract_text() or "").splitlines()
            inicio = next((i for i, l in enumerate(texto) if l.startswith("Clave Concepto de Obra")), -1)
            fin = next((i for i, l in enumerate(texto) if re.fullmatch(r"Página \d+", l.strip())), len(texto))
            lineas.extend(texto[inicio + 1:fin])
    return leer_lineas(lineas)


def leer_lineas(lineas):
    conceptos, grupos = [], {}
    seccion, actual, destino = "GEN", None, None
    for linea in (_PIE.sub("", l).strip() for l in lineas):
        if not linea or re.fullmatch(r"Página \d+", linea) or _PIE_RESTO.match(linea):
            continue
        m = _CLAVE.match(linea)
        if m and m.group(1) in _SECCIONES and not _es_clave_de_concepto(m.group(1)):
            seccion, actual, destino = _SECCIONES[m.group(1)], None, None
            continue
        if m and (_es_clave_de_concepto(m.group(1)) or len(m.group(1)) <= 3):
            clave, resto = m.group(1), m.group(2)
            c = _CONCEPTO.match(resto) if _es_clave_de_concepto(clave) else None
            if c and not c.group(2)[0].isdigit():
                actual = {"clave": clave, "concepto": c.group(1), "unidad": unidad_std(c.group(2)),
                          "pu": _a_numero(c.group(3)), "seccion": seccion,
                          "grupo": _grupo(clave, grupos)}
                conceptos.append(actual)
                destino = actual
            else:
                grupos[clave] = resto
                actual, destino = None, ("grupo", clave)
            continue
        # línea de continuación
        if isinstance(destino, dict):
            destino["concepto"] += " " + linea
        elif destino:
            grupos[destino[1]] += " " + linea
    return [c for c in conceptos if c["pu"] > 0]


def _grupo(clave, grupos):
    """Descripción del encabezado de grupo más cercano (la clave más larga que es prefijo)."""
    for n in range(len(clave) - 1, 0, -1):
        if clave[:n] in grupos:
            return grupos[clave[:n]]
    return ""


def _a_numero(txt):
    try:
        return float(str(txt).replace("$", "").replace(",", "").strip())
    except ValueError:
        return 0.0


# --- Emparejamiento -------------------------------------------------------------

_VACIAS = set("de del la las el los con en a y para por al un una o sin tipo marca modelo "
              "cm mm m ml m2 m3 kg pza no n suministro instalacion prueba colocacion "
              "aplicacion fabricacion material mano obra equipo herramienta necesario "
              "incluye x norma construccion administracion publica ciudad mexico".split())

# Misma cosa escrita distinto en Construbase y en el tabulador.
_SINONIMOS = {"tee": "te", "fofo": "fundido", "fo": "fundido", "tuberia": "tubo",
              "calibre": "cal", "ced": "cedula", "galv": "galvanizado", "pvc": "pvc",
              "conexione": "conexion", "firme": "firme", "vinilica": "vinilica",
              "hidraulico": "hidraulico", "tabicon": "tabicon", "block": "block",
              "bloque": "block", "blocks": "block"}


def palabras(texto):
    """Palabras significativas del núcleo, sin números ni palabras vacías, en singular."""
    salida = set()
    # "tipo M", "tipo L", "tipo K" (cobre), "tipo I"...: la letra distingue el producto
    texto_n = re.sub(r"\btipo\s*[\"']?\s*([a-z])\b[\"']?", r"tipo\1", nucleo(texto))
    for w in re.findall(r"[a-z]+", texto_n):
        if len(w) < 2 or w in _VACIAS:
            continue
        if len(w) > 4 and w.endswith("es"):
            w = w[:-2]
        elif len(w) > 3 and w.endswith("s"):
            w = w[:-1]
        w = _SINONIMOS.get(w, w)
        if w not in _VACIAS:
            salida.add(w)
    return salida


def _idf(documentos):
    n = len(documentos)
    df = collections.Counter(w for d in documentos for w in d)
    return {w: math.log((n + 1) / (c + 1)) + 1 for w, c in df.items()}


def similitud(pal_a, med_a, pal_b, med_b, idf):
    """Jaccard ponderado por IDF (las palabras raras, como 'cobre' o 'block',
    pesan más que 'muro' o 'suministro'), multiplicado por la coincidencia de
    medidas. Devuelve 0-100."""
    union = pal_a | pal_b
    if not union or not pal_a or not pal_b:
        return 0.0
    comun = sum(idf.get(w, 1.0) for w in pal_a & pal_b)
    jaccard = comun / sum(idf.get(w, 1.0) for w in union)
    # contención: cuánto del texto más corto está en el otro (tolera que uno
    # de los dos traiga palabras de más, como la marca o "interiores")
    contencion = comun / min(sum(idf.get(w, 1.0) for w in pal_a), sum(idf.get(w, 1.0) for w in pal_b))
    peso = 0.5 * jaccard + 0.5 * contencion
    if med_a and med_b:
        # Otra medida es otro concepto: 25 mm contra 76 mm no se comparan.
        peso *= len(med_a & med_b) / len(med_a | med_b)
    elif med_a or med_b:
        peso *= 0.7   # solo uno de los dos trae medidas: coincidencia dudosa
    return 100 * peso


def emparejar(conceptos_cb, conceptos_tab, umbral=UMBRAL):
    """Para cada concepto de Construbase, el concepto del tabulador más parecido
    con la misma unidad, si la similitud llega al umbral.

    Candidatos: los conceptos del tabulador con la misma unidad que comparten
    al menos una palabra significativa con el concepto de Construbase."""
    for t in conceptos_tab:
        t["_pal"] = palabras(t["concepto"])
        t["_med"] = medidas(t["concepto"])
    pal_cb = {c["clave"]: palabras(c["descripcion"]) for c in conceptos_cb}
    idf = _idf(list(pal_cb.values()) + [t["_pal"] for t in conceptos_tab])
    indice = collections.defaultdict(lambda: collections.defaultdict(list))
    for i, t in enumerate(conceptos_tab):
        for w in t["_pal"]:
            indice[t["unidad"]][w].append(i)
    resultado = {}
    for c in conceptos_cb:
        pal = pal_cb[c["clave"]]
        por_palabra = indice.get(c["unidad"])
        if not por_palabra or not pal:
            continue
        candidatos = {i for w in pal for i in por_palabra.get(w, [])}
        med = medidas(c["descripcion"])
        mejor = max(((similitud(pal, med, conceptos_tab[i]["_pal"], conceptos_tab[i]["_med"], idf),
                      conceptos_tab[i]) for i in candidatos), key=lambda x: x[0], default=None)
        if mejor and mejor[0] >= umbral:
            resultado[c["clave"]] = (round(mejor[0], 1), mejor[1])
    return resultado


def comparar(conceptos_cb, conceptos_tab, factor_indirectos=FACTOR_SIN_CARGOS):
    """Filas de comparación.

    factor_indirectos divide el P.U. del tabulador para llevarlo a la base de
    Construbase. Por defecto solo quita los cargos adicionales de la CDMX
    (3.627 %), que no aplican en Michoacán; con FACTOR_PU_A_CD se lleva a costo
    directo. Los Básicos (BAS) ya vienen a costo directo y no se dividen."""
    # Se comparan solo el tabulador general y los básicos; se excluyen proyectos
    # y estudios (A), el tabulador atípico (grandes volúmenes) y los reciclados.
    conceptos_tab = [t for t in conceptos_tab
                     if t.get("seccion", "GEN") in ("GEN", "BAS") and not
                     (t.get("seccion", "GEN") == "GEN" and t["clave"].startswith("A"))]
    pares = emparejar(conceptos_cb, conceptos_tab)
    filas = []
    for c in conceptos_cb:
        if c["clave"] not in pares:
            continue
        puntaje, t = pares[c["clave"]]
        cap_tab = t.get("seccion", "GEN")
        cap_tab = capitulo_cdmx(t["clave"]) if cap_tab == "GEN" else cap_tab
        pu_tab = t["pu"] if cap_tab == "BAS" else t["pu"] / factor_indirectos
        cociente = pu_tab / c["pu_act"] if c["pu_act"] else None
        calidad = "muy parecido" if puntaje >= 85 else "parecido (revisar)"
        estado = "congruente" if cociente and RANGO_OK[0] <= cociente <= RANGO_OK[1] else (
            "tabulador más caro" if cociente and cociente > RANGO_OK[1] else "tabulador más barato")
        filas.append({
            "clave_cb": c["clave"], "capitulo": c["capitulo"], "subcapitulo": c["subcapitulo"],
            "clave_gubim": c["gubim"] or "",
            "descripcion_cb": c["descripcion"], "unidad": c["unidad"],
            "pu_2017": c["precio_2017"], "pu_actualizado": c["pu_act"],
            "clave_tabulador": t["clave"], "capitulo_tabulador": CAPITULOS_CDMX.get(cap_tab, cap_tab),
            "concepto_tabulador": t["concepto"],
            "pu_tabulador": round(pu_tab, 2), "similitud": puntaje, "calidad": calidad,
            "cociente": round(cociente, 3) if cociente else "", "estado": estado,
            "mo_estimada": round(c["mo_pct"], 3) if c["mo_pct"] else "",
            "actividad": c["actividad"] or "",
        })
    return filas


def tabulador_disponible():
    pdfs = sorted(REFERENCIAS.glob("tabulador*.pdf"))
    return pdfs[-1] if pdfs else None


def familia(actividad):
    return (actividad or "").split("-")[0]


def grupo(concepto_o_fila):
    """Grupo de ajuste: subcapítulo de Construbase + familia de actividad
    (p. ej. 'TUBERIA Y CONEXIONES FIERRO NEGRO · conexion')."""
    return "{} · {}".format(concepto_o_fila["subcapitulo"], familia(concepto_o_fila["actividad"]))


def comparar_canasta(conceptos_cb, conceptos_tab):
    """Filas de la canasta curada (canasta_cdmx.CANASTA)."""
    from canasta_cdmx import CANASTA

    cb = {c["clave"]: c for c in conceptos_cb}
    tab = {t["clave"]: t for t in conceptos_tab}
    filas = []
    for clave_cb, clave_tab, factor_unidad, equivalencia, nota in CANASTA:
        c, t = cb.get(clave_cb), tab.get(clave_tab)
        if not c or not t:
            continue
        pu_tab = t["pu"] * factor_unidad / FACTOR_SIN_CARGOS
        filas.append({
            "clave_cb": clave_cb, "capitulo": c["capitulo"], "subcapitulo": c["subcapitulo"],
            "clave_gubim": c["gubim"] or "",
            "descripcion_cb": c["descripcion"], "unidad": c["unidad"],
            "pu_2017": c["precio_2017"], "pu_actualizado": c["pu_act"],
            "clave_tabulador": clave_tab, "concepto_tabulador": t["concepto"],
            "pu_tabulador": round(pu_tab, 2), "equivalencia": equivalencia, "nota": nota,
            "cociente": round(pu_tab / c["pu_act"], 3),
            "factor_2017_cdmx": round(pu_tab / c["precio_2017"], 3),
            "actividad": c["actividad"] or "", "mo_estimada": round(c["mo_pct"], 3) if c["mo_pct"] else "",
        })
    return filas


def ajustes_por_grupo(filas, minimo=MINIMO_PARES, tolerancia=TOLERANCIA):
    """{grupo: (n, mediana CDMX/actualizado, ajuste sugerido)}, con grupo =
    subcapítulo + familia de actividad.

    Se sugiere ajuste solo con al menos `minimo` pares y si la mediana se
    aleja más de `tolerancia` de 1; en otro caso el ajuste es 1."""
    grupos = collections.defaultdict(list)
    for f in filas:
        if f["cociente"] != "":
            grupos[grupo(f)].append(f["cociente"])
    salida = {}
    for fam, v in grupos.items():
        med = statistics.median(v)
        sugerido = round(med, 2) if len(v) >= minimo and abs(med - 1) > tolerancia else 1.0
        salida[fam] = (len(v), round(med, 3), sugerido)
    return salida


def evidencia(conceptos_cb, ruta_pdf=None):
    """Lee el tabulador y devuelve (canasta, pares automáticos de similitud alta, ajustes)."""
    ruta_pdf = ruta_pdf or tabulador_disponible()
    tab = leer_tabulador_pdf(ruta_pdf)
    canasta = comparar_canasta(conceptos_cb, tab)
    automaticos = [f for f in comparar(conceptos_cb, tab) if f["similitud"] >= SIMILITUD_ALTA]
    en_canasta = {f["clave_cb"] for f in canasta}
    ajustes = ajustes_por_grupo(canasta + [f for f in automaticos if f["clave_cb"] not in en_canasta])
    return canasta, automaticos, ajustes


def resumir(filas):
    grupos = collections.defaultdict(list)
    for f in filas:
        if f["cociente"] != "":
            grupos[f["capitulo"]].append(f["cociente"])
    return {k: (len(v), statistics.median(v)) for k, v in grupos.items()}


def main(ruta_pdf, factor_indirectos=FACTOR_SIN_CARGOS):
    import generar_tabla

    conceptos, _ = generar_tabla.construir()
    tab = leer_tabulador_pdf(ruta_pdf)
    print(f"Tabulador: {len(tab)} conceptos leídos")
    filas = comparar(conceptos, tab, factor_indirectos)
    print(f"Emparejados: {len(filas)} de {len(conceptos)} conceptos de Construbase")
    SALIDA.mkdir(exist_ok=True)
    with open(SALIDA / "comparacion_tabulador.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]) if filas else ["sin_datos"])
        w.writeheader()
        w.writerows(filas)
    for cap, (n, med) in sorted(resumir(filas).items(), key=lambda kv: kv[1][1]):
        print(f"  {cap:<36} n={n:5d}  tabulador/actualizado mediana={med:.2f}")
    return filas


if __name__ == "__main__":
    main(sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else FACTOR_SIN_CARGOS)
