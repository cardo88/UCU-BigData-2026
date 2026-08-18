# =============================================================================
# PASO 4 - ANÁLISIS DE NEGOCIO: cómo crece el Salario Mínimo Nacional
# =============================================================================
#
# La consigna pide mirar máximos y mínimos, pero en una serie de tiempo
# que casi siempre crece (como un salario mínimo nominal), el máximo y
# el mínimo son casi siempre el último y el primer año: no dicen mucho
# por sí solos. Lo que sí aporta valor de negocio es entender el RITMO
# de crecimiento: ¿crece parejo todos los años, o hay saltos? ¿se está
# desacelerando o acelerando con el tiempo?
#
# Este script:
#   1. Calcula la variación porcentual interanual (cuánto más vale el
#      SMN cada año respecto al anterior).
#   2. Calcula el CAGR (tasa de crecimiento anual compuesta), que resume
#      en un solo número "a qué % constante habría que crecer cada año
#      para pasar del valor inicial al valor final".
#   3. Guarda una tabla ampliada (con la variación interanual) como
#      Parquet, separada del clean, para no mezclar dato curado con
#      dato derivado/calculado.
#   4. Genera un gráfico (PNG) con dos paneles: la evolución del SMN en
#      pesos corrientes, y la variación interanual año a año.
#
# Cómo correr este script (parado en la raíz del repo, con el venv
# activado, y con matplotlib instalado -> pip install matplotlib):
#   python Actividad02/04_analisis_crecimiento.py
# =============================================================================

import matplotlib.pyplot as plt
import pandas as pd

RUTA_PARQUET_CLEAN = "Actividad02/salario_minimo_clean.parquet"
RUTA_PARQUET_ANALISIS = "Actividad02/salario_minimo_analisis.parquet"
RUTA_GRAFICO = "Actividad02/evolucion_salario_minimo.png"

# --- Lectura del dato limpio ---------------------------------------------------
df = pd.read_parquet(RUTA_PARQUET_CLEAN, engine="pyarrow")

# --- 1. Variación interanual (%) ----------------------------------------------
# .pct_change() calcula, para cada fila, la variación porcentual respecto
# a la fila anterior: (valor_actual / valor_anterior - 1) * 100. El
# primer año queda en NaN porque no tiene año anterior con el que
# compararse (no es un error, es esperable).
df["variacion_interanual_%"] = (df["valor"].pct_change() * 100).round(2)

print("Serie completa con variación interanual:")
print(df.to_string(index=False))

# --- 2. Máximo y mínimo (los pide la consigna, aunque aporten poco aquí) ----
fila_min = df.loc[df["valor"].idxmin()]
fila_max = df.loc[df["valor"].idxmax()]
print(
    f"\nMínimo histórico: ${fila_min['valor']:,.0f} en {int(fila_min['año'])}"
)
print(
    f"Máximo histórico: ${fila_max['valor']:,.0f} en {int(fila_max['año'])}"
)
print(
    "-> Como la serie es monótonamente creciente en todo el período, el "
    "mínimo es siempre el primer año y el máximo el último: no son un "
    "hallazgo de negocio en sí, solo confirman que el SMN nunca bajó en "
    "términos nominales."
)

# --- 3. Cómo crece: promedio simple vs. CAGR ----------------------------------
# Promedio simple de las variaciones interanuales: promedia el % de cada
# año, pero le da el mismo peso a un año con salario chico que a uno con
# salario grande.
variaciones = df["variacion_interanual_%"].dropna()
promedio_simple = variaciones.mean()

# CAGR (Compound Annual Growth Rate / tasa de crecimiento anual
# compuesta): a qué tasa constante tendría que haber crecido el SMN,
# todos los años, para pasar de su valor inicial a su valor final en la
# cantidad de años del período. Es la forma correcta de resumir el
# crecimiento de una serie que se compone año a año (como el interés
# compuesto), a diferencia del promedio simple, que puede engañar
# cuando hay saltos grandes puntuales (ver el salto de 2004 a 2005 en
# el resultado impreso más abajo).
valor_inicial = df["valor"].iloc[0]
valor_final = df["valor"].iloc[-1]
anios_transcurridos = df["año"].iloc[-1] - df["año"].iloc[0]
cagr = ((valor_final / valor_inicial) ** (1 / anios_transcurridos) - 1) * 100

print(f"\nPromedio simple de variación interanual: {promedio_simple:.2f}% por año")
print(f"CAGR ({int(df['año'].iloc[0])}-{int(df['año'].iloc[-1])}): {cagr:.2f}% por año")
print(
    "-> El CAGR es más confiable que el promedio simple para resumir el "
    "crecimiento de toda la serie en un solo número, porque no lo "
    "distorsionan saltos puntuales de un año."
)

# --- 4. El mayor salto interanual (para contextualizar el negocio) -----------
idx_max_salto = variaciones.idxmax()
print(
    f"\nMayor salto interanual: {variaciones.loc[idx_max_salto]:.2f}% "
    f"en {int(df.loc[idx_max_salto, 'año'])} "
    f"(pasó de ${df.loc[idx_max_salto - 1, 'valor']:,.0f} "
    f"a ${df.loc[idx_max_salto, 'valor']:,.0f})"
)
print(
    "Este tipo de salto suele reflejar una decisión de política salarial "
    "puntual (ej: un ajuste extraordinario del MTSS), no una tendencia "
    "que se repita todos los años."
)

# --- 5. Guardado de la tabla de análisis (dato derivado, separado del clean) -
df.to_parquet(RUTA_PARQUET_ANALISIS, engine="pyarrow", compression="snappy")
print(f"\nGuardada la tabla de análisis en: {RUTA_PARQUET_ANALISIS}")

# --- 6. Gráfico: evolución del SMN + variación interanual --------------------
# Dos paneles verticales que comparten el eje de años (sharex=True):
#   - Arriba: la línea de evolución del valor nominal del SMN.
#   - Abajo: barras con la variación interanual (%), para ver el RITMO
#     de crecimiento año a año, no solo el nivel acumulado.
fig, (ax_nivel, ax_variacion) = plt.subplots(
    2, 1, figsize=(10, 7), sharex=True, height_ratios=[2, 1]
)

ax_nivel.plot(df["año"], df["valor"], marker="o", color="#2b6cb0")
ax_nivel.set_ylabel("SMN (pesos corrientes)")
ax_nivel.set_title("Evolución del Salario Mínimo Nacional (Uruguay)")
ax_nivel.grid(True, alpha=0.3)

colores_barras = ["#2f855a" if v >= 0 else "#c53030" for v in df["variacion_interanual_%"]]
ax_variacion.bar(df["año"], df["variacion_interanual_%"], color=colores_barras)
ax_variacion.axhline(cagr, color="#2b2b2b", linestyle="--", linewidth=1, label=f"CAGR = {cagr:.1f}%")
ax_variacion.set_ylabel("Variación interanual (%)")
ax_variacion.set_xlabel("Año")
ax_variacion.legend(loc="upper right")
ax_variacion.grid(True, alpha=0.3)

fig.tight_layout()
fig.savefig(RUTA_GRAFICO, dpi=150)
print(f"Guardado el gráfico en: {RUTA_GRAFICO}")
