## Notas de consolidación

La parte se hizo en seis lotes paralelos (2a–2f) con el agente de tarjetas. Al consolidar:

**Insumos y básicos**
- Los insumos de los lotes se integraron a `datos/insumos.csv`, que pasa de 86 a 218. De esos, 74 están validados con rango de mercado y 144 son referencia. No hubo claves repetidas entre lotes.
- Los básicos se integraron a `datos/basicos.json`, que pasa de 8 a 12. Los nuevos son CON-300, CON-350, MOR-ALB-2:7 y YESO-CEM.
- **ALAMBRON-2**: su precio incluía IVA ($20,400/ton, menudeo Home Depot). Se corrigió a $17,586/ton sin IVA y se eliminó el duplicado temporal ALAMBRON-2-SI del lote 2a.
- **POLIET-800**: el lote 2e lo estimó en $9/m², más barato que el calibre 600 cotizado ($11.70/m²). Se escaló por espesor a $15.60/m². Después del cambio se ajustó el rendimiento de E04.09.0008 a 70 m/jor, dentro del rango publicado de 60–120.
- **Sonotubo**: los lotes 2c y 2f usan la misma evidencia (Tool Ferreterías). SONOTUBO-30 y SONOTUBO-40 quedaron en $117 y $160/m.

**Alertas resueltas**
- **Cimbras**: E02.01.0120, 0121, 0123, 0124 y 0129–0132 se agregaron a la canasta CDMX con claves verificadas en el tabulador (CB12BD, CB12BG, CB12BL, CC14BG, CC14BL, CC14BH y CC14BJ). Ahora se validan contra la CDMX y quedan entre +17 % y +25 %. Contra el P.U. actualizado daban entre +30 % y +50 %, porque Construbase subestima la mano de obra de cimbra.
- **E02.01.0121 (cimbra en dados)**: se pasó de 9 a 9.5 m²/jor y de 3.0 a 2.9 pt/m², un 5 % abajo de zapatas. La CDMX usa un solo precio para zapatas, contratrabes y dados.
- **E04.04.0009 (castillo aparente)**: se emparejó con GC31JC, igual que la versión común E04.04.0008.
- **E02.01.0089–0094 (concretos hechos en obra, básicos en mayúsculas)**: Construbase los expresa a costo directo, así que se compara el costo directo de la tarjeta (campo `comparar_costo_directo`).
- **E03.01.0039 y E03.03.0010**: el P.U. del catálogo es erróneo y se usa una `referencia_sustituta` documentada (ver arriba).
- **Tabicón (E04.02.0062–0064)**: queda una desviación de +29 % a +36 %, justificada por el precio regional de la pieza (ver arriba).

**Pendientes para revisión humana**
- Unidad por confirmar:
  - Las boquillas E04.05.0010–0018 se analizaron por metro lineal, aunque el catálogo dice M2.
  - La contratrabe I01.02.0001, la trabe I02.02.0001 y el castillo circular I04.01.0005 se analizaron por pieza, porque su P.U. solo cuadra así.
- Por cotizar en Morelia, en orden de peso en las tarjetas:
  - perfiles de acero (IPR, montén, PTR, ángulo) y lámina;
  - sonotubo de las medidas escaladas;
  - vigueta y bovedilla;
  - Microseal;
  - armex en medidas nuevas;
  - tubo de concreto;
  - vibrocompactador y planta de soldar.

**Claves GuBIM**
- Firmes: los lotes usaron una tabla anterior a la regla de firmes (PR #1). La rama `firme-tarjetas-parte2` (PR #2) pasó los firmes E04.06 a 40.20.10.30 (Recrecidos) y ajustó las alternativas de pisos e impermeabilización. Las alternativas "firme o solera" se quedaron en 20.10.40.10.
- Los cambios de clave de los agentes pasaron a reglas en `scripts/reglas_gubim.py`, así que el catálogo y las tarjetas coinciden en las 522:
  - remates de cubierta (canalón, caballete, casquillo, gotero y remate): 30.20.10.50;
  - registro eléctrico: 50.60.30.50;
  - relleno de tezontle en azotea: 30.20.10.10.
- `--validar-lote` y la reconstrucción de la base ahora señalan toda tarjeta cuyo GuBIM difiera del catálogo.

