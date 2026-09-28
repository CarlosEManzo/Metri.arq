## Notas de consolidación

La parte se hizo en seis lotes (4a–4f). Una primera tanda de agentes se detuvo por el límite de uso sin escribir nada; se relanzó completa con el agente `tarjetas-pu`.

**Insumos**
- Se integraron a `datos/insumos.csv`, que pasa de 724 a 1,059. No hubo claves repetidas; los consumibles de plomería se compartieron entre los lotes 4d, 4e y 4f.
- Los desmontajes (4b y 4c) no llevan materiales: son mano de obra y equipo.

**Validación no independiente (importante)**
- **Precio derivado del catálogo** (estado `derivado del catálogo`), 179 insumos sin precio público:
  - accesorios Jofel;
  - tinas Plasbar;
  - mamparas Sanilock;
  - inodoros, lavabos de pedestal y mingitorios American Standard descontinuados;
  - modelos Helvex descontinuados;
  - 12 tarjas EB Técnica.
- **Rendimiento calibrado al catálogo** (campo nuevo `validacion_no_independiente`):
  - 140 desmontajes del lote 4c;
  - 43 limpiezas y jardinería del lote 4f.
- En estas tarjetas la cercanía con el P.U. actualizado no valida el precio. La auditoría las cuenta y las marca como "no independiente". Son la prioridad para cotizar en Morelia.

**Validación contra CDMX**
- Se agregaron a la canasta 29 pares, verificados contra el tabulador:
  - trazo y demolición de azulejo;
  - desmontaje de tinaco y de bajada de Fo.Fo.;
  - tierra vegetal;
  - 8 tinacos y 3 cisternas Rotoplas;
  - 3 calentadores;
  - 7 accesorios y griferías Helvex;
  - 3 muebles American Standard.
- **Pares que no se cargaron:**
  - lavabos y asientos American Standard, limpiezas, plantas y tala: el tabulador queda entre 40 y 150 % abajo del precio de lista 2026 y de Construbase, lo que parece precio de volumen de obra pública;
  - puertas y ventanas desmontadas (BK15): la CDMX no pica grapas empotradas;
  - bombas Nema: quedan abajo del precio de lista de la bomba sola.
- La diferencia que reportaron los agentes en AF13DB, HI17BQ y HI17BT (PDF contra CSV) no es un error. El CSV guarda el precio sin cargos adicionales: PDF ÷ 1.0376.

**Alertas resueltas en la consolidación**
- **E01.04.0015, demolición de azulejo:** el rendimiento sube de 11 a 14 m²/jor, que es el implícito en CDMX BL12IB (el catálogo usa 20). Queda en +8 % contra la CDMX.
- **E10.03.0158, calentador económico de 38 L:** desviación justificada. El calentador cotizado ya es el 59 % del costo directo CDMX; la tarjeta suma el kit de instalación a gas.

**Alertas abiertas, para decisión humana**
- **E10.02.0036, lavabo Habitat (+187 %) y E10.02.0042, lavabo Veracruz (+132 %).** El precio de lista 2026 ($2,872 y $1,450–2,100 con IVA) ya supera el P.U. del catálogo completo, que trae precios de línea económica de 2017. Hay que cotizar en Morelia o aceptar el precio de lista.
- **E10.03.0152 y 0153, Calorex G-75 (+84 %) y G-100 (+88 %).** El modelo residencial "STD" ya no existe; el equivalente vigente es comercial (75-76 CX y 100-83 CX). Hay que definir qué equipo se especifica.

**GuBIM (reglas nuevas, aplicadas al catálogo y a las tarjetas)**
- Repisa, agarradera, tendedero y destapador: 60.10.10.80, accesorios para cuartos húmedos (antes 50.10.20.60).
- Céspoles, desagües y salidas de tina: 50.20.20.60, terminales de drenaje.
- Los desmontajes conservan 00.20. La clave del sistema retirado va en `gubim_alternativas`, para modelos con fases Existente/Derribado.

**Pendientes para revisión humana**
- **Unidades:**
  - bajadas E01.03.0037–0040 dicen M, pero el precio es por bajada completa de 7 m (llevan `referencia_sustituta` = P.U. ÷ 7);
  - bidet E10.02.0009 y asiento M-147 E10.02.0006, con P.U. del catálogo incoherentes (`referencia_sustituta`).
- **Contenido de E10.03:** no son solo tinacos y calentadores. Incluye 66 accesorios Jofel y 46 tinas de hidromasaje Plasbar.
- **Por cotizar:**
  - equipo: rompedora, compresor, motosierra, canastilla, hamaca, grúa de 25–30 t y sanitario portátil;
  - productos: mamparas Sanilock, tarjas EB, tinas Plasbar, Jofel y plantas.
