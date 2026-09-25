# Auditoría: Construbase 2017 → GuBIMclass v1.2

Revisión de la tabla `salida/Construbase_GuBIM.xlsx`, generada con `scripts/generar_tabla.py`.

## 1. Resumen

| Punto | Resultado |
|---|---|
| Conceptos procesados | 7,272 de 7,272, sin pérdidas |
| Conceptos con clave GuBIM | 7,261; los 11 restantes son insumos (mezclas y morteros) que no se modelan |
| Confianza de la clave | alta 4,050 (56 %) · media 3,089 (42 %) · baja 122 (2 %) |
| Claves GuBIM usadas | 104 de 533; todas existen en el archivo oficial |
| Conceptos con rendimiento | 7,272 (valores de referencia, **no vienen de Construbase**) |
| Rendimientos incongruentes con el precio | 326 (M.O. estimada > 100 % del precio) |
| Precios atípicos | 61 |
| Duplicados con precio distinto | 28 conceptos (14 pares) |
| Fórmulas del Excel | Sin errores (verificado con evaluador independiente) |
| Precio actualizado | Ago-2026, mercado Michoacán, por componentes: factor efectivo 1.60 (provisional hasta capturar el INPP de Morelia) |

## 2. Fuentes

- `construbase.xlsx` y `Datos 2017.xlsx` contienen los **mismos** 7,272 conceptos con los mismos precios. Se usó uno solo (`fuentes/construbase_2017.xlsx`).
- El export es un catálogo sin claves, sin niveles de capítulo y **sin matrices**. Por eso no trae rendimientos, insumos ni el desglose de materiales y mano de obra.
- `GuBIMclass_v.1.2_ES-AssemblyCode.txt` viene en Latin-1. Se guardó una copia en UTF-8 para procesarla (`fuentes/GuBIMclass_v1.2_ES.txt`) y el original intacto para Revit.

## 3. Conciliación con el origen

- Los 7,272 conceptos coinciden uno a uno en descripción, precio y orden con el archivo original.
- La suma de P.U. es $33,062,179.09. El total del archivo ($33,072,373.64) es $10,194.55 mayor porque dos conceptos tienen cantidad distinta de 1:
  - fila 19671: salida eléctrica, cantidad 11
  - fila 27954: despalme, cantidad 2

  El P.U. de ambos es correcto.
- Las claves propias (`E01.01.0001`…) son únicas. Formato: letra de sección, capítulo, subcapítulo y consecutivo.
- La jerarquía se reconstruyó en 3 secciones (Edificación, Urbanización, Base Intelimat) y 30 capítulos. Se descartaron los 3 encabezados "VACIO".
- Se unificaron 124 unidades (`PZA.`→`PZA`, `ML`→`M`, `HRA`/`HOR`→`HR`, `M3K`/`M3/K`→`M3/KM`). La unidad original queda anotada en la alerta de cada concepto.

## 4. Correspondencia con GuBIM

**Método.** Se aplican 162 reglas en orden, sobre capítulo, subcapítulo y descripción. Gana la primera que coincide. Las reglas están en `scripts/reglas_gubim.py`.

**Verificaciones:**
- No hay claves inexistentes.
- Se revisó a mano una muestra aleatoria estratificada de 65 conceptos: 25 de confianza alta, 30 media y 10 baja.
- Se probaron trampas conocidas:
  - "Tinaco" no cae en "Tina".
  - "Mezcladora" no cae en "Mezcla".
  - La coladera de azotea no queda como cubierta.
  - La cubierta de mármol no queda como zoclo.

**Errores encontrados y corregidos durante la auditoría:**
- Tinacos clasificados como tinas (14 conceptos).
- Coladera de azotea clasificada como cubierta.
- Cubierta de mármol para lavabo clasificada como zoclo.
- Motobombas y rotobombas clasificadas como accesorio de baño; ahora son 50.10.10.20.
- Rejilla Irving, tapas y alambre de púas quedaban en la regla general de herrería.
- Dispensadores, basureros y asientos con confianza baja.

**Limitaciones que conviene conocer:**
- **Demoliciones y desmontajes** (412 conceptos) van a `00.20 Preexistencias`, de nivel 2, porque GuBIM no tiene una clave específica de demolición.
- **Concreto, acero y cimbra genéricos** (94 conceptos) quedan en `20.10.10` o `20.20`, porque la descripción no dice a qué elemento pertenecen. En el modelo conviene asignarlos al elemento concreto (zapata, losa, etc.).
- **Confianza media** significa que la clave depende del proyecto:
  - un muro de block puede ser tabique interior (`40.10.10.10`) o fachada (`30.10.10.10`);
  - el agua potable exterior va a `50.10.20.30`, porque GuBIM no tiene red de agua en urbanización;
  - el fierro negro se asignó a gas (`50.40.30.10`).
- Los conceptos se concentran en instalaciones (`50`: 5,179 conceptos). Hay 268 claves GuBIM de nivel 4 sin ningún precio, por ejemplo pilotes, fachadas prefabricadas y ascensores. Construbase no las cubre.

## 5. Rendimientos

**Origen.** Construbase no trae rendimientos. Se asignó un rendimiento de referencia por actividad a cada concepto:
- 186 actividades, 9 tipos de cuadrilla (incluida maquinaria);
- variantes por diámetro, calibre o tamaño;
- basados en la práctica usual mexicana.

La tabla es editable en la hoja **Rendimientos**, y los costos de cuadrilla en **Parámetros**.

**Prueba de congruencia.** Para cada concepto se calcula la mano de obra estimada:
`costo de cuadrilla ÷ rendimiento ÷ P.U. 2017`.
Si pasa de 100 %, la mano de obra sola costaría más que el precio completo, y el rendimiento o el precio está mal.

**Calibración.** La primera versión daba 1,025 conceptos por encima de 100 %:
- Había un error: la palabra "equipo", que aparece en el texto "incluye: ... equipo y herramienta", marcaba piezas chicas como grandes.
- Los rendimientos de piezas chicas eran muy bajos: coples, conexiones, descableado y accesorios de conduit.

Después de corregirlo quedan **326 conceptos a revisar** (hoja Alertas, tipo "Rendimiento a revisar"). Se concentran en:
- instalaciones hidrosanitarias (135): conexiones baratas de cobre, CPVC y PVC;
- preliminares (79): desmontajes de piezas chicas;
- instalación eléctrica (48).

**Mediana de M.O. estimada por capítulo:**

| Capítulo | Mediana |
|---|---|
| Albañilería | 40 % |
| Cimentaciones | 35 % |
| Muros y plafones | 28 % |
| Hidrosanitarias | 26 % |
| Acabados | 15 % |
| Aire acondicionado | 11 % |
| Muebles de baño | 9 % |

Son proporciones razonables: mucha mano de obra en obra negra y poca en equipos y muebles.

**Los rendimientos no están validados contra obra.** 123 conceptos son de maquinaria, así que no se pueden revisar con esta prueba de mano de obra. Antes de usarlos para programar obra se deben contrastar con las matrices de Construbase (si se consigue el export con análisis de P.U.) o con datos propios.

## 6. Precios

- Se buscaron **precios atípicos**: conceptos que se alejan más de 3 veces de la mediana de conceptos similares (mismo subcapítulo, unidad y actividad), con un z robusto mayor a 3.5. Se encontraron 61. Casos a revisar:
  - Desmontaje de bajada de fierro fundido: **$872.65/m** (100 mm) y $1,308.97/m (150 mm). Es 40 a 60 veces el precio de otros desmontajes de tubería. Probable error de captura en Construbase.
  - Granitos azules importados (bahía, macaubas, boquira): $20,900 a $25,600/m². Unas 14 veces la mediana; posiblemente correcto por ser piedra exótica.
  - Plafón Woodworks: $8,845/m², 8.5 veces la mediana.
  - Tee soldable Ced-80 de 350 mm: $40,440, que se explica por el diámetro.
  - Centros de carga I-LINE, de $44,000 a $81,000: se explica por la capacidad.
- **Duplicados con precio distinto** (14 pares). Tienen la misma descripción y distinto precio. Los pares en Urbanización (drenaje contra agua potable) y en puertas de aluminio de Base Intelimat son los más notorios; hay que elegir uno.
- **31 pares de duplicados idénticos** (62 conceptos), es decir, conceptos repetidos en dos capítulos. Solo se reportan en el Catálogo.
- **Actualización.** Ver la sección 7.

## 7. Actualización a 2026 (mercado Michoacán)

**Fuente ideal y por qué no se usó.** El índice que mejor refleja Michoacán es el INPP "Construcción residencial" de **Morelia** (INEGI), que además trae los componentes de materiales, mano de obra y maquinaria. La red de este entorno bloquea inegi.org.mx, cmic.org.mx y banxico.org.mx. Por eso se usaron búsquedas web y se contrastaron varias fuentes.

**Fuentes consultadas** (detalle en la hoja *Fuentes* del Excel):

| Fuente | Dato | Factor sep-2017 → ago-2026 |
|---|---|---|
| INPC nacional (INEGI) | 96.09 → 145.462 | 1.51 (piso: inflación general) |
| INPC Michoacán | 3.77 % anual en ago-2026, contra 3.26 % nacional | algo mayor que el nacional |
| Construcción residencial nacional (CEICO/INEGI) | 2023 +3.94 %, 2024 +3.93 %, 2025 +4.52 %; materias primas +29 % de 2020 a 2022 | 1.60–1.70 (estimado; faltan 2017–2022 exactos) |
| Mano de obra Michoacán (CONASAMI, Indeed Morelia) | Oficial ≈ $560/día en 2026 contra $350–400 en 2017; mínimo general $80 → $315 | ≈ 1.65 |
| Materiales (cemento, varilla, cable, cobre) | Cemento ≈ 1.2x; varilla ≈ 1.5x; cable +17 % solo en 2025 | ≈ 1.60 |

**Método elegido (el más cercano al mercado de Michoacán).** Se actualiza por componentes:

`P.U. 2026 = P.U. 2017 × [ %M.O. × 1.65 + (1 − %M.O.) × 1.60 ]`

- %M.O. es la mano de obra estimada del concepto (cuadrilla ÷ rendimiento), con un tope de 60 %.
- El resultado es un factor efectivo de **1.600 a 1.618** según el capítulo, **1.602** en conjunto.
- En Michoacán la mano de obra subió más que los materiales por los aumentos al salario mínimo. Con este método, los conceptos de mucha mano de obra (excavación manual, aplanados, cimbra) suben un poco más.

**Contraste con precios de mercado 2026:**
- Muro de block de 15 cm: **$419/m²** en la tabla, contra $420–480/m² instalado según referencias de mercado.
- Concreto f'c=250 colocado: **$3,502/m³** en la tabla, contra $2,400–2,900/m³ solo el suministro. La diferencia corresponde a colocación, vibrado, acarreos e indirectos, así que es coherente.

**Limitaciones:**
- Los factores son **estimaciones**, no el índice oficial de Morelia. En cuanto se capture el INPP de Morelia (sep-2017 y último mes) en *Parámetros*, sustituye a este cálculo.
- Un factor por componente no distingue entre materiales: el acero y el cobre subieron más que el cemento.
- La separación entre mano de obra y materiales depende de rendimientos de referencia sin validar.

## 8. Verificación del Excel

- LibreOffice no funciona en este contenedor. Las fórmulas se evaluaron con `pycel`, un evaluador independiente, sobre 450 filas al azar.
- Se probaron los modos de actualización: por índices INPP (factor 1.655), por factor manual (1.5 y 1.7) y por componentes (materiales 1.60, M.O. 1.65). En el método por componentes, el Excel coincide al centavo con el cálculo en Python en 200 filas al azar.
- Resultado: **0 errores**. P.U. actualizado, rendimiento, jornadas, horas-hombre y % de M.O. calculan bien. La única diferencia que apareció fue de redondeo en la propia prueba en Python; Excel redondea correctamente.
- El libro tiene activado el recálculo completo al abrir.

## 9. Pendientes recomendados

1. Capturar el INPP de "Construcción residencial" de **Morelia** (sep-2017 y último mes) en la hoja Parámetros.
2. Ajustar el costo de las cuadrillas en Parámetros al salario real de la zona (Querétaro o Morelia).
3. Revisar las 326 alertas de rendimiento y los 14 pares duplicados.
4. Validar los rendimientos sin tarjetas de P.U. de Construbase. Opciones, de la más rápida a la más sólida:
   - Contrastar con el Tabulador General de Precios Unitarios de la CDMX (público, actualización mensual 2026) y con tabuladores de dependencias (SICT, IMSS, INIFECH).
   - Tomar rendimientos de bibliografía de costos (Suárez Salazar, *Costo y tiempo en edificación*; Varela, *Ingeniería de costos*).
   - Medirlos en obra propia (por ejemplo Casa Querétaro): unidades hechas por jornada de cada cuadrilla.
   - Pedir a quien tenga licencia de Construbase/Neodata el reporte "análisis de precios unitarios" solo de los conceptos que más se usen.
5. Validar con un proyecto real (por ejemplo Casa Querétaro) que las claves GuBIM coinciden con el Assembly Code usado en Revit.
