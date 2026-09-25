"""Genera la tabla Construbase -> GuBIMclass con precios y rendimientos.

Salidas (carpeta salida/):
  Construbase_GuBIM.xlsx  libro de trabajo con fórmulas editables
  construbase_gubim.csv   misma tabla en texto plano (valores a precio 2017)

Uso:  python3 scripts/generar_tabla.py
"""
import collections
import csv
import math
import statistics
from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

import leer_construbase
import reglas_gubim
import rendimientos
from reglas_gubim import normalizar

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "salida"
GUBIM = RAIZ / "fuentes" / "GuBIMclass_v1.2_ES.txt"

LETRA_SECCION = {"Edificación": "E", "Urbanización": "U", "Base Intelimat": "I"}
MO_ALERTA = 1.0     # mano de obra estimada > 100 % del precio
Z_ATIPICO = 3.5     # z robusto (log del precio) dentro de subcapítulo, unidad y actividad
VECES_ATIPICO = 3   # y además a más de 3 veces (o menos de 1/3) de la mediana

ENCABEZADO = Font(bold=True, color="FFFFFF")
FONDO_ENC = PatternFill("solid", fgColor="1F4E78")
FONDO_PARAM = PatternFill("solid", fgColor="FFF2CC")


def leer_gubim():
    gub = {}
    for linea in GUBIM.read_text(encoding="utf-8").splitlines():
        partes = linea.split("\t")
        if len(partes) >= 3:
            gub[partes[0]] = (partes[1], int(partes[2]))
    return gub


def asignar_claves(conceptos):
    """Clave propia: letra de sección + nº capítulo + nº subcapítulo + consecutivo."""
    caps, subs, cont = {}, {}, collections.Counter()
    for c in conceptos:
        kc = (c["seccion"], c["capitulo"])
        caps.setdefault(kc, len([k for k in caps if k[0] == c["seccion"]]) + 1)
        ks = kc + (c["subcapitulo"],)
        subs.setdefault(ks, len([k for k in subs if k[:2] == kc]) + 1)
        cont[ks] += 1
        c["clave"] = "{}{:02d}.{:02d}.{:04d}".format(
            LETRA_SECCION[c["seccion"]], caps[kc], subs[ks], cont[ks])


def detectar_alertas(conceptos):
    # Precios atípicos: se compara cada concepto con los de su mismo
    # subcapítulo, unidad y actividad (p. ej. excavaciones con excavaciones).
    grupos = collections.defaultdict(list)
    for c in conceptos:
        grupos[(c["seccion"], c["capitulo"], c["subcapitulo"], c["unidad"],
                (c["actividad"] or "").split("-")[0])].append(c)
    for grupo in grupos.values():
        if len(grupo) < 5:
            continue
        logs = [math.log(c["precio_2017"]) for c in grupo]
        med = statistics.median(logs)
        mad = statistics.median(abs(x - med) for x in logs)
        if mad == 0:
            continue
        for c, x in zip(grupo, logs):
            z = 0.6745 * (x - med) / mad
            veces = math.exp(x - med)
            if abs(z) > Z_ATIPICO and not 1 / VECES_ATIPICO < veces < VECES_ATIPICO:
                c["alertas"].append(
                    "Precio atípico: {:.1f}x la mediana de conceptos similares ({})".format(
                        veces, "alto" if z > 0 else "bajo"))
    # Descripciones repetidas.
    rep = collections.defaultdict(list)
    for c in conceptos:
        rep[(normalizar(c["descripcion"]), c["unidad"])].append(c)
    for grupo in rep.values():
        if len(grupo) < 2:
            continue
        precios = {c["precio_2017"] for c in grupo}
        otras = ", ".join(c["clave"] for c in grupo)
        for c in grupo:
            if len(precios) > 1:
                c["alertas"].append("Duplicado con precio distinto: " + otras)
            else:
                c["alertas"].append("Duplicado idéntico: " + otras)
    for c in conceptos:
        if c["unidad"] != c["unidad_origen"].upper():
            c["alertas"].append("Unidad normalizada ({} -> {})".format(c["unidad_origen"], c["unidad"]))
        if c["confianza"] == "baja":
            c["alertas"].append("Clave GuBIM genérica: revisar")


def construir():
    conceptos = leer_construbase.leer()
    gub = leer_gubim()
    asignar_claves(conceptos)
    for c in conceptos:
        c["gubim"], c["confianza"] = reglas_gubim.clasificar(c)
        c["actividad"], c["actividad_desc"], c["cuadrilla"], c["rendimiento"] = rendimientos.asignar(c)
        c["alertas"] = []
        costo = rendimientos.CUADRILLAS[c["cuadrilla"]][2] if c["cuadrilla"] else None
        c["mo_pct"] = costo / c["rendimiento"] / c["precio_2017"] if costo else None
    detectar_alertas(conceptos)
    return conceptos, gub


def encabezar(ws, columnas, anchos):
    ws.append(columnas)
    for i, ancho in enumerate(anchos, start=1):
        celda = ws.cell(row=1, column=i)
        celda.font, celda.fill = ENCABEZADO, FONDO_ENC
        celda.alignment = Alignment(wrap_text=True, vertical="center")
        ws.column_dimensions[get_column_letter(i)].width = ancho
    ws.freeze_panes = "A2"


def hoja_leame(wb, n):
    ws = wb.active
    ws.title = "Léame"
    ws.column_dimensions["A"].width = 120
    lineas = [
        ("Construbase 2017 → GuBIMclass v1.2: precios y rendimientos", True),
        ("", False),
        ("Hojas", True),
        ("Parámetros: índices INPP para actualizar precios y costo por jornada de las cuadrillas (celdas amarillas).", False),
        (f"Catálogo: los {n} conceptos con clave propia, clave GuBIM, precio 2017, precio actualizado y rendimiento.", False),
        ("Rendimientos: tabla de actividades con cuadrilla y rendimiento (unidades por jornada de 8 h). Editable.", False),
        ("GuBIM: las 533 claves de GuBIMclass con el número de conceptos asignados a cada una.", False),
        ("Resumen: estadísticas de precio por capítulo y reparto de la confianza de la clave GuBIM.", False),
        ("Alertas: conceptos a revisar (precio atípico, duplicados, mano de obra estimada mayor al precio, clave genérica).", False),
        ("", False),
        ("Cómo actualizar los precios", True),
        ("1. Descarga del INEGI el Índice Nacional de Precios Productor, 'Construcción residencial' (o 'Edificación').", False),
        ("2. Captura en Parámetros el valor de septiembre 2017 y el del mes más reciente. El factor y la columna", False),
        ("   'P.U. actualizado' se calculan solos. También puedes escribir un factor manual.", False),
        ("", False),
        ("Rendimientos: importante", True),
        ("El export de Construbase NO incluye las matrices de precios unitarios, por lo tanto no trae rendimientos.", False),
        ("Los rendimientos de esta tabla son valores de referencia de la práctica mexicana, asignados por tipo de", False),
        ("actividad y diámetro. Son un punto de partida para programar obra (4D) y deben validarse con las matrices", False),
        ("de Construbase o con datos propios de obra. La columna '% M.O. estimada' compara el costo de la cuadrilla", False),
        ("con el precio 2017: si supera 100 % el rendimiento o el precio es incongruente y se debe revisar.", False),
        ("", False),
        ("Confianza de la clave GuBIM", True),
        ("alta: el concepto identifica el elemento GuBIM. media: se deduce del contexto (p. ej. un muro puede ser", False),
        ("interior o de fachada). baja: clave genérica del capítulo. insumo: mezclas y concretos básicos que no se modelan.", False),
        ("", False),
        ("Uso con Revit", True),
        ("La clave GuBIM es el Assembly Code de Revit. Filtra el Catálogo por la clave del elemento para elegir el", False),
        ("concepto de precio; las horas-hombre por unidad sirven para estimar duraciones en la programación de obra.", False),
        ("", False),
        ("Generado con scripts/generar_tabla.py a partir de fuentes/construbase_2017.xlsx y fuentes/GuBIMclass_v1.2_ES.txt.", False),
    ]
    for texto, negrita in lineas:
        ws.append([texto])
        ws.cell(row=ws.max_row, column=1).font = Font(bold=negrita, size=13 if negrita else 11)


def hoja_parametros(wb):
    ws = wb.create_sheet("Parámetros")
    ws.column_dimensions["A"].width = 48
    ws.column_dimensions["B"].width = 16
    ws.column_dimensions["C"].width = 70
    filas = [
        ("Actualización de precios", None, None),
        ("INPP Construcción residencial, sep-2017", None, "Capturar valor INEGI (misma base que el actual)"),
        ("INPP Construcción residencial, mes actual", None, "Capturar valor INEGI del mes más reciente"),
        ("Factor manual (opcional)", None, "Si se captura, sustituye al cálculo con INPP"),
        ("Factor de actualización", '=IF(B5<>"",B5,IF(AND(N(B3)>0,N(B4)>0),B4/B3,""))', "Se aplica a todos los P.U. 2017"),
        ("Mes/año del precio actualizado", None, "Referencia informativa, p. ej. ago-2026"),
    ]
    ws.append(["Parámetro", "Valor", "Nota"])
    for f in filas:
        ws.append(list(f))
    for r in (3, 4, 5, 7):
        ws.cell(row=r, column=2).fill = FONDO_PARAM
    ws.cell(row=2, column=1).font = Font(bold=True)
    ws.cell(row=6, column=1).font = Font(bold=True)
    ws["B6"].number_format = "0.0000"
    for c in ws[1]:
        c.font, c.fill = ENCABEZADO, FONDO_ENC

    ws.append([])
    ws.append(["Cuadrillas (costo por jornada, salario real con FSR)", None, None])
    ws.cell(row=ws.max_row, column=1).font = Font(bold=True)
    ws.append(["Clave", "Personas", "Descripción", "Costo jornada 2017"])
    fila_ini = ws.max_row + 1
    for clave, (desc, personas, costo) in rendimientos.CUADRILLAS.items():
        ws.append([clave, personas, desc, costo])
        ws.cell(row=ws.max_row, column=4).fill = FONDO_PARAM
        ws.cell(row=ws.max_row, column=4).number_format = "$#,##0.00"
    ws.column_dimensions["D"].width = 20
    return "Parámetros!$B$6", "Parámetros!$A${}:$D${}".format(fila_ini, ws.max_row)


def hoja_rendimientos(wb):
    ws = wb.create_sheet("Rendimientos")
    encabezar(ws, ["Actividad", "Descripción", "Unidad", "Cuadrilla", "Rendimiento (u/jornada)",
                   "Jornadas por unidad", "Fuente"], [28, 55, 9, 10, 14, 12, 40])
    for (fam, u, tam), (desc, cuad, rend) in rendimientos.ACTIVIDADES.items():
        clave = "-".join(p for p in (fam, u, tam) if p)
        fila = ws.max_row + 1
        ws.append([clave, desc, u, cuad, rend, f"=1/E{fila}",
                   "Referencia típica, por validar con matrices u obra"])
        ws.cell(row=fila, column=5).fill = FONDO_PARAM
        ws.cell(row=fila, column=6).number_format = "0.0000"
    ws.auto_filter.ref = ws.dimensions
    return "Rendimientos!$A$2:$E${}".format(ws.max_row)


def hoja_catalogo(wb, conceptos, gub, celda_factor, rango_cuad, rango_rend):
    ws = wb.create_sheet("Catálogo")
    cols = ["Clave CB", "Sección", "Capítulo", "Subcapítulo", "Descripción", "Unidad",
            "P.U. 2017", "P.U. actualizado", "Clave GuBIM", "Descripción GuBIM", "Nivel",
            "Confianza", "Actividad", "Cuadrilla", "Rendimiento (u/jornada)",
            "Jornadas por unidad", "Horas-hombre por unidad", "% M.O. estimada",
            "Alertas", "Fila origen"]
    encabezar(ws, cols, [13, 12, 20, 22, 70, 7, 12, 13, 12, 34, 6, 9, 22, 8, 12, 11, 11, 10, 50, 8])
    for c in conceptos:
        f = ws.max_row + 1
        desc_g, nivel = gub.get(c["gubim"], ("", None)) if c["gubim"] else ("", None)
        act = c["actividad"] or ""
        ws.append([
            c["clave"], c["seccion"], c["capitulo"], c["subcapitulo"], c["descripcion"], c["unidad"],
            c["precio_2017"],
            f'=IF({celda_factor}="","",ROUND(G{f}*{celda_factor},2))',
            c["gubim"] or "", desc_g, nivel, c["confianza"], act, c["cuadrilla"] or "",
            f'=IFERROR(VLOOKUP(M{f},{rango_rend},5,0),"")' if act else "",
            f'=IF(O{f}="","",1/O{f})' if act else "",
            f'=IF(O{f}="","",VLOOKUP(N{f},{rango_cuad},2,0)*8/O{f})' if act else "",
            (f'=IF(OR(O{f}="",VLOOKUP(N{f},{rango_cuad},4,0)=""),"",'
             f'VLOOKUP(N{f},{rango_cuad},4,0)/O{f}/G{f})') if act else "",
            "; ".join(c["alertas"]), c["fila_origen"],
        ])
        for col, fmt in ((7, "$#,##0.00"), (8, "$#,##0.00"), (16, "0.0000"),
                         (17, "0.00"), (18, "0%")):
            ws.cell(row=f, column=col).number_format = fmt
    ultima = ws.max_row
    ws.auto_filter.ref = f"A1:T{ultima}"
    rojo = PatternFill("solid", fgColor="F8CBAD")
    ws.conditional_formatting.add(f"R2:R{ultima}", CellIsRule(operator="greaterThan", formula=["1"], fill=rojo))
    dv = DataValidation(type="list", formula1='"alta,media,baja,insumo"', allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(f"L2:L{ultima}")


def hoja_gubim(wb, conceptos, gub):
    ws = wb.create_sheet("GuBIM")
    encabezar(ws, ["Clave GuBIM", "Descripción", "Nivel", "Conceptos asignados",
                   "P.U. 2017 mediano", "Unidad más frecuente"], [14, 60, 7, 12, 14, 12])
    por_clave = collections.defaultdict(list)
    for c in conceptos:
        if c["gubim"]:
            por_clave[c["gubim"]].append(c)
    for clave, (desc, nivel) in gub.items():
        lista = por_clave.get(clave, [])
        unidad = collections.Counter(c["unidad"] for c in lista).most_common(1)
        med = statistics.median(c["precio_2017"] for c in lista if c["unidad"] == unidad[0][0]) if lista else None
        ws.append([clave, "   " * (nivel - 1) + desc, nivel, len(lista), med, unidad[0][0] if unidad else ""])
        ws.cell(row=ws.max_row, column=5).number_format = "$#,##0.00"
        if nivel == 1:
            for cel in ws[ws.max_row]:
                cel.font = Font(bold=True)
    ws.auto_filter.ref = ws.dimensions


def hoja_resumen(wb, conceptos):
    ws = wb.create_sheet("Resumen")
    encabezar(ws, ["Sección", "Capítulo", "Conceptos", "P.U. mínimo", "P.U. mediano", "P.U. máximo",
                   "Confianza alta", "Confianza media", "Confianza baja", "Insumo",
                   "Alertas de precio", "M.O. > 100 %"], [14, 34, 10, 12, 12, 14, 10, 10, 10, 8, 10, 10])
    grupos = collections.defaultdict(list)
    for c in conceptos:
        grupos[(c["seccion"], c["capitulo"])].append(c)
    for (sec, cap), lista in grupos.items():
        precios = [c["precio_2017"] for c in lista]
        conf = collections.Counter(c["confianza"] for c in lista)
        ws.append([sec, cap, len(lista), min(precios), statistics.median(precios), max(precios),
                   conf["alta"], conf["media"], conf["baja"], conf["insumo"],
                   sum(any(a.startswith(("Precio atípico", "Duplicado con")) for a in c["alertas"]) for c in lista),
                   sum(1 for c in lista if c["mo_pct"] and c["mo_pct"] > MO_ALERTA)])
        for col in (4, 5, 6):
            ws.cell(row=ws.max_row, column=col).number_format = "$#,##0.00"
    total = ws.max_row
    ws.append(["TOTAL", "", f"=SUM(C2:C{total})", "", "", "", f"=SUM(G2:G{total})", f"=SUM(H2:H{total})",
               f"=SUM(I2:I{total})", f"=SUM(J2:J{total})", f"=SUM(K2:K{total})", f"=SUM(L2:L{total})"])
    for cel in ws[ws.max_row]:
        cel.font = Font(bold=True)


def hoja_alertas(wb, conceptos):
    ws = wb.create_sheet("Alertas")
    encabezar(ws, ["Clave CB", "Tipo", "Detalle", "Capítulo", "Subcapítulo", "Descripción", "Unidad",
                   "P.U. 2017", "% M.O. estimada"], [13, 26, 50, 20, 22, 70, 7, 12, 10])
    for c in conceptos:
        filas = []
        for a in c["alertas"]:
            tipo = a.split(":")[0].split(" (")[0]
            if tipo in ("Unidad normalizada", "Duplicado idéntico"):
                continue
            filas.append((tipo, a))
        if c["mo_pct"] and c["mo_pct"] > MO_ALERTA:
            filas.append(("Rendimiento a revisar",
                          "M.O. estimada {:.0%} del precio con {} = {} {}/jornada".format(
                              c["mo_pct"], c["cuadrilla"], c["rendimiento"], c["unidad"])))
        for tipo, det in filas:
            ws.append([c["clave"], tipo, det, c["capitulo"], c["subcapitulo"], c["descripcion"],
                       c["unidad"], c["precio_2017"], c["mo_pct"]])
            ws.cell(row=ws.max_row, column=8).number_format = "$#,##0.00"
            ws.cell(row=ws.max_row, column=9).number_format = "0%"
    ws.auto_filter.ref = ws.dimensions


def escribir_csv(conceptos, gub):
    with open(SALIDA / "construbase_gubim.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["clave_cb", "seccion", "capitulo", "subcapitulo", "descripcion", "unidad",
                    "pu_2017", "clave_gubim", "descripcion_gubim", "confianza", "actividad",
                    "cuadrilla", "rendimiento_u_jornada", "horas_hombre_u", "mo_estimada_pct", "alertas"])
        for c in conceptos:
            hh = (rendimientos.CUADRILLAS[c["cuadrilla"]][1] * 8 / c["rendimiento"]) if c["rendimiento"] else ""
            w.writerow([c["clave"], c["seccion"], c["capitulo"], c["subcapitulo"], c["descripcion"],
                        c["unidad"], c["precio_2017"], c["gubim"] or "",
                        gub.get(c["gubim"], ("",))[0] if c["gubim"] else "", c["confianza"],
                        c["actividad"] or "", c["cuadrilla"] or "", c["rendimiento"] or "",
                        round(hh, 4) if hh != "" else "",
                        round(c["mo_pct"], 3) if c["mo_pct"] else "", "; ".join(c["alertas"])])


def main():
    SALIDA.mkdir(exist_ok=True)
    conceptos, gub = construir()
    wb = Workbook()
    hoja_leame(wb, len(conceptos))
    celda_factor, rango_cuad = hoja_parametros(wb)
    rango_rend = hoja_rendimientos(wb)
    hoja_catalogo(wb, conceptos, gub, celda_factor, rango_cuad, rango_rend)
    hoja_gubim(wb, conceptos, gub)
    hoja_resumen(wb, conceptos)
    hoja_alertas(wb, conceptos)
    wb.move_sheet("Catálogo", offset=-2)
    wb.calculation.fullCalcOnLoad = True
    wb.save(SALIDA / "Construbase_GuBIM.xlsx")
    escribir_csv(conceptos, gub)
    conf = collections.Counter(c["confianza"] for c in conceptos)
    print(f"{len(conceptos)} conceptos; confianza {dict(conf)}")
    print("Claves GuBIM usadas:", len({c['gubim'] for c in conceptos if c['gubim']}))
    print("Con rendimiento:", sum(1 for c in conceptos if c["rendimiento"]))
    print("M.O. > 100 %:", sum(1 for c in conceptos if c["mo_pct"] and c["mo_pct"] > MO_ALERTA))


if __name__ == "__main__":
    main()
