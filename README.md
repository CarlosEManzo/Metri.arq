# Metri.arq

Herramientas de costos de Métrica Estudio R&P para presupuestar desde modelos BIM.

## Construbase → GuBIMclass

Tabla que une el catálogo de precios unitarios **Construbase 2017** con la clasificación **GuBIMclass v1.2**, que en Revit es el *Assembly Code*. A cada concepto le agrega un rendimiento y el tiempo de ejecución estimado.

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
- Para actualizar precios no hace falta regenerar: se capturan los índices INPP en la hoja *Parámetros* del Excel.

> Los rendimientos **no vienen de Construbase**, porque el export no trae las matrices de precios unitarios. Son valores de referencia por validar; ver `AUDITORIA.md`.
