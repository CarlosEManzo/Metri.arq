"""Lee el export de Construbase (catálogo en formato "presupuesto") y lo
convierte en una tabla limpia con sección, capítulo y subcapítulo.

El export no trae códigos ni niveles: todos los encabezados tienen el mismo
formato. Los capítulos se reconocen por nombre dentro de cada sección.
"""
from pathlib import Path
import re

import openpyxl

RAIZ = Path(__file__).resolve().parent.parent
ARCHIVO = RAIZ / "fuentes" / "construbase_2017.xlsx"

# Encabezados que abren una nueva sección del catálogo.
SECCIONES = {
    "TERRACERIAS": "Urbanización",
    "Base Intelimat": "Base Intelimat",
}

CAPITULOS = {
    "Edificación": {
        "PRELIMINARES", "CIMENTACIONES", "ESTRUCTURA", "ALBAÑILERIA",
        "MUROS Y PLAFONES", "ACABADOS", "HERRERIA", "ALUMINIO", "CARPINTERIA",
        "MUEBLES DE BAÑO", "INSTALACIONES HIDROSANITARIAS",
        "INSTALACION ELECTRICA", "AIRE ACONDICIONADO",
        "SISTEMAS CONTRA INCENDIO", "LIMPIEZAS", "JARDINERIA",
    },
    "Urbanización": {
        "TERRACERIAS", "DRENAJE (EXCAVACIONES Y RELLENOS)", "AGUA POTABLE",
        "PAVIMENTOS",
    },
    "Base Intelimat": {
        "CIMENTACION", "ESTRUCTURA DE CONCRETO", "ESTRUCTURA METALICA",
        "ALBAÑILERIA", "MUROS Y PLAFONES", "ACABADOS", "HERRERIA", "ALUMINIO",
        "MUEBLES DE BAÑO",
    },
}

UNIDADES = {
    "PZA.": "PZA", "ML": "M", "HRA": "HR", "HOR": "HR", "M3K": "M3/KM",
    "M3/K": "M3/KM",
}


def normalizar_unidad(u):
    u = str(u).strip().upper()
    return UNIDADES.get(u, u)


def limpiar(texto):
    return re.sub(r"\s+", " ", str(texto)).strip()


def leer(archivo=ARCHIVO):
    ws = openpyxl.load_workbook(archivo, read_only=True, data_only=True).worksheets[0]
    seccion, capitulo, subcapitulo = "Edificación", None, None
    conceptos = []
    for fila, r in enumerate(ws.iter_rows(values_only=True), start=1):
        desc = r[1] if len(r) > 1 else None
        if not desc:
            continue
        es_concepto = isinstance(r[4], (int, float)) and r[2]
        if not es_concepto:
            if any(c is not None for c in r[2:]) or r[0] is not None:
                continue  # encabezado de columnas o total
            nombre = limpiar(desc)
            if nombre == "VACIO":
                continue
            if nombre in SECCIONES and SECCIONES[nombre] != seccion:
                seccion = SECCIONES[nombre]
                if nombre == "Base Intelimat":
                    capitulo = subcapitulo = None
                    continue
            if nombre in CAPITULOS[seccion] and nombre != capitulo:
                capitulo, subcapitulo = nombre, None
            else:
                subcapitulo = nombre
            continue
        conceptos.append({
            "fila_origen": fila,
            "seccion": seccion,
            "capitulo": capitulo,
            "subcapitulo": subcapitulo or capitulo,
            "descripcion": limpiar(desc),
            "unidad": normalizar_unidad(r[2]),
            "unidad_origen": str(r[2]).strip(),
            "precio_2017": float(r[4]),
        })
    return conceptos


if __name__ == "__main__":
    import collections
    c = leer()
    print(len(c), "conceptos")
    cont = collections.Counter((x["seccion"], x["capitulo"], x["subcapitulo"]) for x in c)
    for k, v in cont.items():
        print(v, *k, sep=" | ")
