"""Factores para llevar los precios de Construbase (sep-2017) a 2026, mercado Michoacán.

El índice ideal es el INPP "Construcción residencial" de Morelia (INEGI), con
sus componentes de materiales, mano de obra y maquinaria. Mientras no se
capture en el Excel, se usa una actualización por componentes:

    P.U. actualizado = P.U. 2017 x [ %MO x FACTOR_MO + (1 - %MO) x FACTOR_MATERIALES ]

donde %MO es la mano de obra estimada del concepto (cuadrilla / rendimiento),
limitada a TOPE_MO. Así los conceptos de mucha mano de obra, que en Michoacán
subieron más por los aumentos al salario mínimo, se actualizan más que los de
puro material o equipo.

Los factores son estimaciones con las fuentes de FUENTES; se editan en la hoja
Parámetros del Excel sin regenerar.
"""

FACTOR_MATERIALES = 1.60   # materiales y equipo, sep-2017 -> ago-2026
FACTOR_MO = 1.65           # mano de obra (salario real de cuadrilla), Michoacán
TOPE_MO = 0.60             # % máximo de mano de obra que se reconoce en un P.U.
PERIODO = "sep-2017 → ago-2026"

INPC_SEP_2017 = 96.09      # base 2a quincena jul-2018 = 100 (aprox., verificar)
INPC_AGO_2026 = 145.462    # INEGI, boletín INPC agosto 2026

# (fuente, dato, uso)
FUENTES = [
    ("INEGI – INPC agosto 2026", "145.462 puntos; inflación anual 3.26 %",
     "Piso del factor: INPC sep-2017 → ago-2026 = {:.3f}".format(INPC_AGO_2026 / INPC_SEP_2017)),
    ("INEGI – INPC Michoacán agosto 2026", "Inflación anual 3.77 % (5a más alta del país)",
     "Michoacán sube algo más que el promedio nacional"),
    ("CEICO/CMIC con datos INEGI – construcción residencial nacional", "Dic–dic: 2023 +3.94 %, 2024 +3.93 %, 2025 +4.52 %",
     "Construcción residencial 2023–2025 ≈ INPC"),
    ("CEICO/CMIC – componentes 2025", "Materiales +4.28 %, mano de obra +5.98 %, maquinaria +1.34 %",
     "La mano de obra sube más rápido que los materiales"),
    ("CEICO/CMIC – materias primas construcción residencial", "+29.36 % de mar-2020 a dic-2022",
     "2020–2022 los materiales superaron al INPC (+18 % en el mismo periodo)"),
    ("CONASAMI – salarios mínimos", "General 2017 $80.04 → 2026 $315.04; oficial de albañilería 2026 $363.44 (resto del país)",
     "El piso salarial del peón casi se cuadruplicó"),
    ("Indeed – sueldo de albañil en Morelia 2026", "$14,560/mes ≈ $560/día",
     "Mano de obra de mercado en Morelia"),
    ("Referencias de mercado 2017–2018", "Albañil $350–400/día; ayudante $200–250/día",
     "Mano de obra 2017 → factor ≈ 1.6; con aumento del FSR (vacaciones 2023, cuotas IMSS) ≈ 1.65"),
    ("Cemento gris 50 kg", "ene-2017 ≈ $215 (Monterrey, menudeo); 2026 $240–280 (+$20 en 2026)",
     "Cemento ≈ 1.2x"),
    ("Varilla corrugada 3/8\"", "2026 ≈ $20,500/ton (Ternium, GASA)",
     "Acero ≈ 1.5x (precio 2017 no confirmado en fuentes)"),
]
