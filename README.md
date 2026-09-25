# Metri.arq

Herramientas de costos de Métrica Estudio R&P para presupuestar desde modelos BIM.

## Construbase → GuBIMclass

Tabla que une el catálogo de precios unitarios **Construbase 2017** con la clasificación **GuBIMclass v1.2**, que en Revit es el *Assembly Code*. A cada concepto le agrega el precio actualizado a 2026 para Michoacán, un rendimiento y el tiempo de ejecución estimado.

| Archivo | Contenido |
|---|---|
| `salida/Construbase_GuBIM.xlsx` | Libro de trabajo: catálogo con clave GuBIM, precio 2017, precio actualizado (fórmula), rendimiento, horas-hombre y alertas |
| `salida/construbase_gubim.csv` | La misma tabla en texto (UTF-8), para importar a otras herramientas |
| `AUDITORIA.md` | Revisión de resultados, limitaciones y pendientes |
| `fuentes/` | Archivos de origen (no se suben al repositorio, ver abajo) |
| `scripts/` | Código que genera la tabla |

### Regenerar

Los datos de Construbase tienen licencia, así que ni `fuentes/` ni `salida/` se suben al repositorio. Para regenerar, copia en `fuentes/`:

- `construbase_2017.xlsx`: export de Construbase (catálogo "Estándar código auxiliar").
- `GuBIMclass_v1.2_ES.txt`: GuBIMclass v1.2 Assembly Code, convertido a UTF-8 (`iconv -f latin1 -t utf-8`).

```bash
pip install -r requirements.txt
python3 scripts/generar_tabla.py
```

- Las reglas de correspondencia están en `scripts/reglas_gubim.py`.
- Los rendimientos de referencia están en `scripts/rendimientos.py`.
- Los factores de actualización y sus fuentes están en `scripts/actualizacion.py`.
- Para cambiar la actualización no hace falta regenerar: en la hoja *Parámetros* del Excel se editan los factores de materiales y de mano de obra, o se captura el INPP de Morelia.

### Comparar contra el tabulador de la CDMX

```bash
pip install -r requirements.txt
python3 scripts/comparar_tabulador.py referencias/tabulador_cdmx_2026-07.pdf
```

Si hay un tabulador en `referencias/`, `generar_tabla.py` agrega la hoja *Tabulador CDMX* y la columna *P.U. con ajuste CDMX*. La canasta curada de conceptos de vivienda está en `scripts/canasta_cdmx.py`.

Empareja cada concepto con el más parecido del Tabulador General de Precios Unitarios de la CDMX (misma unidad y mismas medidas) y compara precios. El resultado queda en `salida/comparacion_tabulador.csv`.

> Los rendimientos **no vienen de Construbase**, porque el export no trae las matrices de precios unitarios. Son valores de referencia por validar; ver `AUDITORIA.md`.

## Tarjetas de precio unitario con GuBIMclass

Cada concepto puede tener su tarjeta de análisis de P.U.: materiales (con básicos desglosados), mano de obra (cuadrilla y rendimiento), herramienta y equipo, indirectos 15 %, financiamiento 1.5 % y utilidad 10 %. Cada tarjeta lleva su clave GuBIMclass.

| Archivo | Contenido |
|---|---|
| `tarjetas/<clave>.json` | Definición de cada tarjeta: insumos, cantidades, cuadrilla, rendimiento y supuestos |
| `datos/insumos.csv` | Precios de insumos puestos en obra, con fuente, fecha y estado de validación |
| `datos/basicos.json` | Morteros y concretos hechos en obra, desglosados por m³ |
| `datos/parametros_tarjeta.json` | Porcentajes, zona, fecha base y salarios reales por categoría |
| `.claude/agents/tarjetas-pu.md` | Agente que elabora y valida las tarjetas |
| `salida/tarjetas.sqlite`, `salida/Base_tarjetas_PU.xlsx` | Base de datos con todas las tarjetas (local) |

```bash
python3 scripts/tarjeta_pu.py                    # reconstruye la base de datos
python3 scripts/tarjeta_pu.py --validar E04.02.0033
python3 scripts/tarjeta_pu.py --pendientes ALBAÑILERIA
python3 scripts/tarjeta_pu.py --pdf E04.02.0033  # PDF y Excel de una tarjeta, solo bajo pedido
```

Para el PDF hace falta Playwright con Chromium (`pip install playwright`). Las fuentes IBM Plex (licencia OFL) están en `plantillas/fuentes/`.

**Validación de cada tarjeta.** Se compara contra el P.U. actualizado de Construbase y contra el tabulador de la CDMX cuando hay un par. Una diferencia mayor a ±25 % genera una alerta. También se muestra el rendimiento que implica el precio de la CDMX.
