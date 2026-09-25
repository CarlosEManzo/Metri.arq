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
    return re.sub(r"[^a-z0-9/.=]+", " ", t).strip()


def medidas(texto):
    return {m.replace(",", ".").replace(" ", "") for m in _NUM.findall(nucleo(texto))}


def unidad_std(u):
    u = normalizar(u).strip().replace(".", "")
    return UNIDADES.get(u, u.upper())


# --- Lectura del PDF ----------------------------------------------------------

_PRECIO = re.compile(r"\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2}))\s*$")
_CLAVE = re.compile(r"^([A-Z0-9]{1,6}(?:[.\-][A-Z0-9]{1,6}){1,6})\s+(.*)$")


def leer_tabulador_pdf(ruta):
    """Devuelve [{clave, concepto, unidad, pu}] a partir del PDF del tabulador.

    Primero intenta leer tablas; si la página no trae tablas reconocibles,
    reconstruye los conceptos línea por línea (clave al inicio, precio al final).
    """
    import pdfplumber

    conceptos = []
    with pdfplumber.open(ruta) as pdf:
        for pagina in pdf.pages:
            tablas = pagina.extract_tables() or []
            filas = [f for t in tablas for f in t if f and len(f) >= 4]
            if filas:
                conceptos.extend(_de_tablas(filas))
            else:
                conceptos.extend(_de_lineas((pagina.extract_text() or "").splitlines()))
    return [c for c in conceptos if c["pu"] > 0 and c["concepto"]]


def _a_numero(txt):
    try:
        return float(str(txt).replace("$", "").replace(",", "").strip())
    except ValueError:
        return 0.0


def _de_tablas(filas):
    salida, actual = [], None
    for fila in filas:
        celdas = [(c or "").strip() for c in fila]
        clave, concepto, unidad, pu = celdas[0], " ".join(celdas[1:-2]), celdas[-2], celdas[-1]
        if normalizar(clave).startswith("clave"):
            continue
        if clave and _a_numero(pu):
            actual = {"clave": clave, "concepto": concepto, "unidad": unidad_std(unidad), "pu": _a_numero(pu)}
            salida.append(actual)
        elif actual and concepto and not clave:
            actual["concepto"] += " " + concepto   # continuación de la descripción
    return salida


def _de_lineas(lineas):
    salida, pendiente = [], None
    for linea in lineas:
        linea = linea.strip()
        m = _CLAVE.match(linea)
        if m:
            pendiente = {"clave": m.group(1), "texto": m.group(2)}
        elif pendiente:
            pendiente["texto"] += " " + linea
        else:
            continue
        p = _PRECIO.search(pendiente["texto"])
        if p:
            resto = pendiente["texto"][:p.start()].strip().split()
            if resto:
                unidad = resto.pop()
                salida.append({"clave": pendiente["clave"], "concepto": " ".join(resto),
                               "unidad": unidad_std(unidad), "pu": _a_numero(p.group(1))})
            pendiente = None
    return salida


# --- Emparejamiento -------------------------------------------------------------

_VACIAS = set("de del la las el los con en a y para por al un una o sin tipo marca modelo "
              "cm mm m ml m2 m3 kg pza no n".split())


def palabras(texto):
    """Palabras significativas del núcleo, sin números ni palabras vacías, en singular."""
    salida = set()
    for w in re.findall(r"[a-z]+", nucleo(texto)):
        if len(w) < 2 or w in _VACIAS:
            continue
        if len(w) > 4 and w.endswith("es"):
            w = w[:-2]
        elif len(w) > 3 and w.endswith("s"):
            w = w[:-1]
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
    if not union:
        return 0.0
    peso = sum(idf.get(w, 1.0) for w in pal_a & pal_b) / sum(idf.get(w, 1.0) for w in union)
    if med_a and med_b:
        # Otra medida es otro concepto: 25 mm contra 76 mm no se comparan.
        peso *= len(med_a & med_b) / len(med_a | med_b)
    elif med_a or med_b:
        peso *= 0.7   # solo uno de los dos trae medidas: coincidencia dudosa
    return 100 * peso


def emparejar(conceptos_cb, conceptos_tab, umbral=UMBRAL):
    """Para cada concepto de Construbase, el concepto del tabulador más parecido
    con la misma unidad, si la similitud llega al umbral."""
    por_unidad = collections.defaultdict(list)
    for t in conceptos_tab:
        t["_nucleo"] = nucleo(t["concepto"])
        t["_pal"] = palabras(t["concepto"])
        t["_med"] = medidas(t["concepto"])
        por_unidad[t["unidad"]].append(t)
    pal_cb = {c["clave"]: palabras(c["descripcion"]) for c in conceptos_cb}
    idf = _idf(list(pal_cb.values()) + [t["_pal"] for t in conceptos_tab])
    resultado = {}
    for c in conceptos_cb:
        candidatos = por_unidad.get(c["unidad"])
        if not candidatos:
            continue
        # preselección rápida por texto, luego puntaje fino
        preseleccion = process.extract(nucleo(c["descripcion"]), [t["_nucleo"] for t in candidatos],
                                       scorer=fuzz.token_set_ratio, limit=15)
        med = medidas(c["descripcion"])
        mejor = max(((similitud(pal_cb[c["clave"]], med, candidatos[i]["_pal"], candidatos[i]["_med"], idf),
                      candidatos[i]) for _, _, i in preseleccion), key=lambda x: x[0], default=None)
        if mejor and mejor[0] >= umbral:
            resultado[c["clave"]] = (round(mejor[0], 1), mejor[1])
    return resultado


def comparar(conceptos_cb, conceptos_tab, factor_indirectos=FACTOR_SIN_CARGOS):
    """Filas de comparación.

    factor_indirectos divide el P.U. del tabulador para llevarlo a la base de
    Construbase. Por defecto solo quita los cargos adicionales de la CDMX
    (3.627 %), que no aplican en Michoacán; con FACTOR_PU_A_CD se lleva a costo
    directo. Los Básicos (BAS) ya vienen a costo directo y no se dividen."""
    pares = emparejar(conceptos_cb, conceptos_tab)
    filas = []
    for c in conceptos_cb:
        if c["clave"] not in pares:
            continue
        puntaje, t = pares[c["clave"]]
        cap_tab = capitulo_cdmx(t["clave"])
        pu_tab = t["pu"] if cap_tab == "BAS" else t["pu"] / factor_indirectos
        cociente = pu_tab / c["pu_act"] if c["pu_act"] else None
        calidad = "muy parecido" if puntaje >= 85 else "parecido (revisar)"
        estado = "congruente" if cociente and RANGO_OK[0] <= cociente <= RANGO_OK[1] else (
            "tabulador más caro" if cociente and cociente > RANGO_OK[1] else "tabulador más barato")
        filas.append({
            "clave_cb": c["clave"], "capitulo": c["capitulo"], "clave_gubim": c["gubim"] or "",
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
