## Notas de consolidación

La parte se hizo en siete lotes paralelos (3a–3g) con el agente de tarjetas.

**Insumos y básicos**
- Se integraron a `datos/insumos.csv`, que pasa de 218 a 724 insumos, y a `datos/basicos.json`, que pasa de 12 a 18 básicos. No hubo claves repetidas entre lotes. Los cristales, herrajes y consumibles compartidos se coordinaron entre los lotes 3d, 3f y 3g.
- **Estado nuevo, `derivado del catálogo`.** Lo llevan los 255 insumos cuyo precio, o la diferencia entre modelos, sale del P.U. de Construbase:
  - 142 alfombras;
  - 74 piedras (mármol y granito);
  - vinílicos, mosaicos de color, cantera, barro y plafones modulares.
  Sus tarjetas quedan cerca del P.U. actualizado por construcción, así que esa comparación no las valida de forma independiente. El resumen cuenta cuántas tarjetas tienen más de la mitad del material derivado del catálogo; en la tabla van marcadas como "material derivado del catálogo". **Son la prioridad para cotizar en Morelia.**

**Validación contra CDMX**
- Se agregaron 48 pares a la canasta, todos verificados contra el tabulador:
  - 13 de muros y plafones de tablaroca y Durock;
  - 5 de básicos de mortero y concreto;
  - 12 de loseta y zoclo vinílico;
  - 3 de adocreto;
  - 3 de pisos y muros de Porcelanite;
  - 1 de alfombra Sprint;
  - 2 de esmalte;
  - 5 de domos con ventila;
  - 2 de cristal de 6 mm.
- Con ellos, la parte queda con 52 tarjetas validadas contra la CDMX.
- **Básicos:** el tabulador publica sus Básicos (BAS) a costo directo. Las tarjetas con `comparar_costo_directo` ahora comparan su costo directo también contra la CDMX, así que los morteros E02.01.0148–0151 ya no necesitan `cdmx_no_comparable`.

**Alertas resueltas en la consolidación**
- **E06.05.0008, esmalte en plafón:** el rendimiento pasa de 25 a 30 m²/jor, con la misma relación plafón/muro de las vinílicas (40/45). La CDMX usa un solo precio para muros y plafones.
- **Morteros E04.01.0007 (1:1:8) y E04.01.0003 (1:0.25:3):** desviación justificada con cifras. En el 1:1:8, los materiales ya son el 87 % del costo directo de la CDMX y la diferencia es la elaboración con revolvedora. El 1:0.25:3 es una mezcla más rica que su par de la CDMX, el 1:0.25:4.
- **Cristal claro y bronce de 6 mm:** la CDMX implica un cristal de unos $330–380/m². El mercado 2026 está más arriba: CostoNet da $678/m² sin IVA y el rango publicado es $400–650. Las tarjetas usan $400 y $450.

**Alerta abierta, para decisión humana**
- **E04.01.0002, mezcla yeso-cemento-agua: +71 % a costo directo.** El básico YESO-CEM lleva 900 kg de yeso por m³, que es físicamente coherente: un bulto de 40 kg cubre ≈3 m² a 1.5 cm, o sea ≈890 kg/m³. El precio del catálogo solo cuadra con ≈540 kg/m³. El yeso está a precio de menudeo ($2.93/kg de Home Depot); con una cotización de mayoreo en Morelia la diferencia baja, pero no desaparece. Hay que decidir si se ajusta la dosificación, el precio del yeso o se acepta la diferencia.

**Claves GuBIM (reglas nuevas en `scripts/reglas_gubim.py`, aplicadas al catálogo y a las tarjetas)**
- Muros "compuesto por 1 panel" (forro de una cara, que la CDMX llama lambrín): 40.10.10.30 Trasdosados.
- Teja de barro: 30.20.10.40 Acabados de cubiertas.
- Pintura de tráfico: 40.40.10.30 Señalización de suelos.
- La regla de revestimientos ya no confunde "pegazulejo" con azulejo: E06.02.0039, piso de barro, pasa a 40.20.20.20.
- La clave anterior de cada tarjeta cambiada quedó en `gubim_alternativas`.
- Quedan solo como alternativas en las tarjetas, porque dependen del uso:
  - cancel con puerta de 2.2–2.4 m en fachada: 30.10.20.20;
  - rejilla Irving en exterior;
  - escalón de escalera marina.

**Pendientes para revisión humana**
- **Unidades:**
  - zoclo de cantera E06.04.0032: el catálogo dice M2, se analizó por M;
  - barandales E08.04: PZA, analizados como 1 m.
- **Duplicados del catálogo:**
  - E09.05.0001–0008 repiten E09.01.0001–0008;
  - I08.03.0005, 0008, 0011 y 0014 se leyeron como la versión con cierrapuertas.
- **Muro de sillar E06.04.0001 (−49 %):** confirmar qué pieza quiso decir Construbase con "block de tepetate".
- **Por cotizar, en este orden:**
  - piedras (mármol y granito) con marmolerías de Morelia;
  - alfombras;
  - lista de Corev (31 tarjetas);
  - perfil de aluminio por kg;
  - cristales especiales y domos;
  - plafones modulares Armstrong;
  - maderas finas.
