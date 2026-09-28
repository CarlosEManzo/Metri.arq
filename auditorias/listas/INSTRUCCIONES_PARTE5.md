# Instrucciones comunes para los lotes de la Parte 5 (instalaciones hidrosanitarias)

Sigue `.claude/agents/tarjetas-pu.md`. Además:

**Trabajo en paralelo** (hay varios agentes a la vez):
- NO corras `git pull`, `generar_tabla.py` ni la reconstrucción de la base (`python3 scripts/tarjeta_pu.py` sin argumentos). No generes PDF, no hagas commits.
- Escribe solo:
  - `tarjetas/<clave>.json` de tu lista;
  - `datos/insumos_lote5X.csv` (tu letra), con las mismas columnas que `datos/insumos.csv`: clave, descripcion, unidad, precio, fuente, fecha, estado;
  - si hace falta, `datos/basicos_lote5X.json`.
- NO edites `datos/insumos.csv`, `datos/basicos.json`, los scripts ni las tarjetas de otras claves.
- Antes de crear un insumo, búscalo con grep en `datos/insumos.csv` y en `datos/insumos_lote5*.csv` y reúsalo si existe.
- La clave GuBIM es la del catálogo (`salida/construbase_gubim.csv`, columna `clave_gubim`). Otras opciones van en `gubim_alternativas`.

**Cómo trabajar (lotes grandes):**
1. Lee el catálogo de tus claves:
   `python3 -c "import csv;L=open('auditorias/listas/parte_5X.txt').read().split();[print(r['clave_cb'],r['unidad'],r['pu_actualizado'],r['descripcion'][:150]) for r in csv.DictReader(open('salida/construbase_gubim.csv',encoding='utf-8-sig')) if r['clave_cb'] in L]"`
2. Mira 2–3 tarjetas terminadas como ejemplo: `tarjetas/E11.03.0001.json` (fierro negro, recién hecha) y `tarjetas/E11.01.0023.json` (cobre, de la canasta).
3. Escribe **un script de Python** en `/tmp/claude-0/-home-user-Metri-arq/67aa2765-a490-59ee-9a40-1b93b94192e7/scratchpad/gen5X.py`. El script genera todas las tarjetas por familia, con tablas de precio por diámetro y rendimiento por diámetro, y escribe tu CSV de insumos. Así, si te cortan, se regenera todo.
4. Escribe las tarjetas **pronto**, aunque sean preliminares, y después afínalas.
5. Valida con `python3 scripts/tarjeta_pu.py --validar-lote auditorias/listas/parte_5X.txt` hasta tener 0 errores. Revisa las alertas.

**Precios:**
- Sin IVA, 2026. Busca con WebSearch (Home Depot, fabricantes, distribuidores).
- Si escalas por diámetro a partir de dos anclas, márcalo `referencia` y anota la regla en `fuente`.
- Evita `derivado del catálogo`: úsalo solo si no hay nada público, y dilo.

**Rendimientos de referencia (plomero + ayudante):**
- Tubo, en m/jor según diámetro: 13–25 mm 30–40; 32–50 mm 20–28; 64–100 mm 10–16; 150 mm o más, 6–10.
- Conexiones, en pza/jor: 13–25 mm 14–20; 32–50 mm 8–12; 64–100 mm 4–8.
- Válvulas: como las conexiones, un poco menos.

**Alertas:**
- Si el par CDMX automático no es comparable, usa `"cdmx_no_comparable": "<razón>"`.
- Entre ±25 y ±50 % con una causa concreta con cifras, usa `"desviacion_justificada"`.
- Arriba de ±50 %, corrige.
- Si calibras al catálogo sin otra fuente, marca `"validacion_no_independiente"`.

**Reporte final (corto):**
- tabla por familia con el rango de P.U. y de diferencias;
- insumos nuevos (cuántos validados y cuántos referencia);
- rendimientos;
- pares CDMX no cargados;
- alertas que quedan;
- cuántas tarjetas quedaron sin validación independiente.
