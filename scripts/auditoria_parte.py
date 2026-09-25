"""Informe de auditoría de una parte (lote) de tarjetas.

Uso:
    python3 scripts/auditoria_parte.py <numero> "<titulo>" CLAVE [CLAVE ...]
    python3 scripts/auditoria_parte.py <numero> "<titulo>" --lista archivo.txt

Lee salida/tarjetas.sqlite (reconstruir antes con `python3 scripts/tarjeta_pu.py`) y
escribe auditorias/parte_<numero>.md con: resumen, tabla por tarjeta contra las
referencias, alertas, pares CDMX no comparables, insumos usados que siguen como
referencia y rendimientos.
"""
import sqlite3
import statistics
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
BASE = RAIZ / "salida" / "tarjetas.sqlite"
DESTINO = RAIZ / "auditorias"


def pct(x):
    return "" if x is None else f"{x:+.1%}"


def mx(x):
    return "" if x is None else f"{x:,.2f}"


def informe(numero, titulo, claves):
    con = sqlite3.connect(BASE)
    con.row_factory = sqlite3.Row
    marcas = ",".join("?" for _ in claves)
    tarjetas = con.execute(f"SELECT * FROM tarjetas WHERE clave_cb IN ({marcas}) ORDER BY clave_cb", claves).fetchall()
    faltan = sorted(set(claves) - {t["clave_cb"] for t in tarjetas})
    insumos_ref = con.execute(
        f"""SELECT m.clave, m.descripcion, m.unidad, i.precio, i.fuente, COUNT(DISTINCT m.clave_cb) AS n
            FROM materiales m JOIN insumos i ON i.clave = m.clave
            WHERE m.clave_cb IN ({marcas}) AND m.tipo != 'basico' AND i.estado = 'referencia'
            GROUP BY m.clave ORDER BY n DESC""", claves).fetchall()

    difs = [t["dif_vs_cdmx"] if t["referencia_validacion"] == "CDMX" else t["dif_vs_actualizado"]
            for t in tarjetas if t["referencia_validacion"]]
    alertas = [t for t in tarjetas if t["alerta"]]
    no_comp = [t for t in tarjetas if t["cdmx_no_comparable"]]
    justif = [t for t in tarjetas if t["desviacion_justificada"]]
    lineas = [
        f"# Auditoría parte {numero}: {titulo}",
        "",
        f"Generado el {date.today():%Y-%m-%d} desde `salida/tarjetas.sqlite`. Todas las tarjetas son borradores del "
        "agente de tarjetas, pendientes de revisión humana.",
        "",
        "## Resumen",
        "",
        "| Punto | Resultado |",
        "|---|---|",
        f"| Tarjetas | {len(tarjetas)} de {len(claves)} |",
        f"| Con alerta (±25 % contra su referencia) | {len(alertas)} |",
        f"| Validadas contra CDMX | {sum(1 for t in tarjetas if t['referencia_validacion'] == 'CDMX')} |",
        f"| Validadas contra P.U. actualizado | {sum(1 for t in tarjetas if t['referencia_validacion'] == 'P.U. actualizado')} |",
        f"| Par CDMX no comparable (con razón) | {len(no_comp)} |",
        f"| Desviación > ±25 % justificada | {len(justif)} |",
        f"| Diferencia mediana contra su referencia | {pct(statistics.median(difs)) if difs else '—'} |",
        f"| Insumos usados que siguen como referencia | {len(insumos_ref)} |",
        "",
    ]
    if faltan:
        lineas += ["**Sin tarjeta:** " + ", ".join(faltan), ""]
    lineas += [
        "## Tarjetas",
        "",
        "| Clave | GuBIM | Concepto | Unidad | P.U. tarjeta | P.U. actualizado | P.U. CDMX | Dif. vs act. | Dif. vs CDMX | Validada contra | Alerta |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for t in tarjetas:
        lineas.append(
            f"| {t['clave_cb']} | {t['gubim']} | {t['descripcion'][:60]} | {t['unidad']} | {mx(t['pu'])} | "
            f"{mx(t['pu_actualizado'])} | {mx(t['pu_cdmx'])} | {pct(t['dif_vs_actualizado'])} | {pct(t['dif_vs_cdmx'])} | "
            f"{t['referencia_validacion']} | {t['alerta'] or '—'} |")
    lineas += ["", "## Composición y rendimiento", "",
               "| Clave | Materiales | M.O. | Herr./equipo | Cuadrilla | Rendimiento | HH/unidad | Rend. implícito CDMX |",
               "|---|---|---|---|---|---|---|---|"]
    for t in tarjetas:
        cd = t["costo_directo"] or 1
        lineas.append(
            f"| {t['clave_cb']} | {t['materiales'] / cd:.0%} | {t['mano_obra'] / cd:.0%} | {t['herramienta_equipo'] / cd:.0%} | "
            f"{t['cuadrilla']} | {t['rendimiento']} | {t['hh_por_unidad']} | {t['rendimiento_implicito_cdmx'] or '—'} |")
    if no_comp:
        lineas += ["", "## Pares CDMX no comparables", ""]
        lineas += [f"- **{t['clave_cb']}**: {t['cdmx_no_comparable']}" for t in no_comp]
    if justif:
        lineas += ["", "## Desviaciones justificadas (±25 % a ±50 %)", ""]
        lineas += [f"- **{t['clave_cb']}** ({pct(t['dif_vs_cdmx'] if t['referencia_validacion'] == 'CDMX' else t['dif_vs_actualizado'])}): {t['desviacion_justificada']}" for t in justif]
    if alertas:
        lineas += ["", "## Alertas abiertas", ""]
        lineas += [f"- **{t['clave_cb']}**: {t['alerta']}" for t in alertas]
    if insumos_ref:
        lineas += ["", "## Insumos por cotizar (estado: referencia)", "",
                   "| Insumo | Descripción | Unidad | Precio | Tarjetas | Fuente |", "|---|---|---|---|---|---|"]
        lineas += [f"| {i['clave']} | {i['descripcion']} | {i['unidad']} | {mx(i['precio'])} | {i['n']} | {i['fuente']} |"
                   for i in insumos_ref]
    lineas += ["", "## Supuestos por tarjeta", ""]
    lineas += [f"- **{t['clave_cb']}**: {t['supuestos'] or '—'}" for t in tarjetas]
    DESTINO.mkdir(exist_ok=True)
    ruta = DESTINO / f"parte_{int(numero):02d}.md"
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    return ruta, len(tarjetas), len(alertas)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    numero, titulo, resto = sys.argv[1], sys.argv[2], sys.argv[3:]
    if resto[0] == "--lista":
        resto = [x.strip() for x in Path(resto[1]).read_text().split() if x.strip()]
    ruta, n, a = informe(numero, titulo, resto)
    print(f"{ruta.relative_to(RAIZ)}: {n} tarjetas, {a} alertas")
