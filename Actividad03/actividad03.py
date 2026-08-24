# =============================================================================
# ACTIVIDAD 3 - METRICAS: SALARIO MINIMO NACIONAL E IPC
# =============================================================================
#
# Este script:
#   1. Lee el salario minimo nacional desde el Parquet limpio de Actividad 2.
#   2. Lee el IPC general del archivo oficial del INE.
#   3. Limpia y normaliza ambas fuentes para poder conectarlas por año.
#   4. Calcula minimo, maximo y promedio del salario minimo.
#   5. Calcula una metrica combinada: crecimiento real aproximado del
#      salario minimo, descontando la variacion anual del IPC.
#
# El Excel del INE contiene varias filas de titulo antes de los encabezados.
# En este archivo, la fila 7 contiene los encabezados reales.
#
# Como ejecutar, desde la raiz del repositorio y con el venv activado:
#   python Actividad03/actividad03.py
#
# Dependencias:
#   pip install pandas pyarrow openpyxl matplotlib
# =============================================================================

import re
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


RUTA_SALARIO = Path("Actividad02/salario_minimo_clean.parquet")
RUTA_IPC = Path("Actividad03/IPC gral y variaciones_base 2022.xlsx")
RUTA_IPC_ANUAL = Path("Actividad03/ipc_anual.parquet")
RUTA_METRICAS = Path("Actividad03/salario_ipc_metricas.parquet")


def numero_uruguayo(valor):
    """Convierte numeros con formato uruguayo a float."""
    if pd.isna(valor):
        return None

    texto = str(valor).strip().replace("%", "")
    if not texto:
        return None

    # Los valores del archivo pueden venir como 1.234,56 o 1234,56.
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")

    texto = re.sub(r"[^0-9.\-]", "", texto)
    if not texto or texto in {".", "-", "-."}:
        return None

    try:
        return float(texto)
    except ValueError:
        return None


def leer_salario_minimo():
    """Lee el Parquet limpio generado por Actividad 2."""
    if not RUTA_SALARIO.exists():
        raise FileNotFoundError(
            f"No existe {RUTA_SALARIO}. Ejecuta primero "
            "python Actividad02/03_limpieza.py."
        )

    salario = pd.read_parquet(RUTA_SALARIO, engine="pyarrow")
    salario = salario.rename(columns={"valor": "salario_minimo"})
    columnas_requeridas = {"año", "salario_minimo"}
    if not columnas_requeridas.issubset(salario.columns):
        raise ValueError(
            f"El Parquet debe contener las columnas {columnas_requeridas}. "
            f"Columnas encontradas: {list(salario.columns)}"
        )

    salario = salario[["año", "salario_minimo"]].dropna()
    return salario.sort_values("año").reset_index(drop=True)


def leer_ipc():
    """Lee y normaliza el IPC general mensual del archivo del INE."""
    # En este archivo la fila 7 contiene los encabezados reales (la portada
    # ocupa las filas 0 a 4 y hay filas auxiliares antes de los datos).
    ipc_crudo = pd.read_excel(RUTA_IPC, header=7)
    ipc_crudo = ipc_crudo.dropna(how="all").copy()

    # La estructura oficial es: Mes y año, Índice, Mensual, Acum. año,
    # Acum.12 meses, Trimestre, Cuatrimestre y Semestre.
    ipc = pd.DataFrame(
        {
            "periodo": ipc_crudo.iloc[:, 0],
            "indice_general": ipc_crudo.iloc[:, 1],
            "ipc_ultimos_12_meses": ipc_crudo.iloc[:, 4],
        }
    )
    ipc = ipc.dropna(how="all").copy()

    # El periodo viene como una fecha mensual, por ejemplo 1937-07-01. Al
    # venir ya como fecha real (no como texto ni como numero serial de
    # Excel), alcanza con pedirle el año a pandas directamente.
    ipc["periodo"] = pd.to_datetime(ipc["periodo"], errors="coerce")
    ipc["año"] = ipc["periodo"].dt.year
    ipc["indice_general"] = ipc["indice_general"].map(numero_uruguayo)
    ipc["ipc_ultimos_12_meses"] = ipc["ipc_ultimos_12_meses"].map(numero_uruguayo)

    ipc = ipc.dropna(subset=["año", "indice_general"])
    ipc["año"] = ipc["año"].astype(int)

    # Para comparar años completos se toma diciembre de cada año. Si el
    # archivo usa otra etiqueta, el ultimo registro disponible cumple el
    # mismo objetivo para ese año.
    ipc_anual = (
        ipc.sort_values(["año", "periodo"])
        .groupby("año", as_index=False)
        .tail(1)
        .sort_values("año")
        .reset_index(drop=True)
    )
    ipc_anual["variacion_ipc_anual_%"] = (
        ipc_anual["indice_general"].pct_change() * 100
    )

    # Si el INE ya provee la variacion de los ultimos doce meses, se conserva
    # como referencia; la variacion calculada permite trabajar con cualquier
    # version equivalente de la planilla.
    ipc_anual.to_parquet(RUTA_IPC_ANUAL, engine="pyarrow", index=False)
    print(f"Archivo IPC anual generado: {RUTA_IPC_ANUAL}")
    return ipc_anual


def generar_grafica(datos):
    """Genera una gráfica de variaciones y crecimiento real aproximado."""
    figura, ejes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    ejes[0].plot(
        datos["año"],
        datos["variacion_salario_%"],
        marker="o",
        label="Salario mínimo",
        color="#1f77b4",
    )
    ejes[0].plot(
        datos["año"],
        datos["variacion_ipc_anual_%"],
        marker="o",
        label="IPC",
        color="#d62728",
    )
    ejes[0].axhline(0, color="black", linewidth=0.8)
    ejes[0].set_ylabel("Variación anual (%)")
    ejes[0].set_title("Variación anual del salario mínimo y del IPC")
    ejes[0].legend()
    ejes[0].grid(alpha=0.3)

    colores = [
        "#2ca02c" if valor >= 0 else "#d62728"
        for valor in datos["crecimiento_real_aprox_%"].fillna(0)
    ]
    ejes[1].bar(
        datos["año"],
        datos["crecimiento_real_aprox_%"],
        color=colores,
    )
    ejes[1].axhline(0, color="black", linewidth=0.8)
    ejes[1].set_xlabel("Año")
    ejes[1].set_ylabel("Crecimiento real (%)")
    ejes[1].set_title("Crecimiento real aproximado del salario mínimo")
    ejes[1].grid(axis="y", alpha=0.3)

    figura.tight_layout()
    figura.savefig("Actividad03/analisis_salario_ipc.png", dpi=150)
    plt.close(figura)
    print("Gráfica generada: Actividad03/analisis_salario_ipc.png")


def main():
    salario = leer_salario_minimo()
    leer_ipc()
    ipc = pd.read_parquet(RUTA_IPC_ANUAL, engine="pyarrow")

    print("\nMETRICAS DEL SALARIO MINIMO NACIONAL")
    print(f"Minimo: ${salario['salario_minimo'].min():,.2f}")
    print(f"Maximo: ${salario['salario_minimo'].max():,.2f}")
    print(f"Promedio: ${salario['salario_minimo'].mean():,.2f}")

    # El salario minimo del indicador 10454 rige desde el 1° de enero de
    # cada año (ver README de Actividad 2). Su variacion interanual, por
    # lo tanto, cubre el periodo entre el 1° de enero del año N-1 y el 1°
    # de enero del año N, es decir: aproximadamente el año calendario N-1
    # completo. Para comparar peras con peras, hay que usarla contra la
    # inflacion de ESE mismo periodo (el IPC del año N-1), no contra el
    # IPC de diciembre del año N, que todavia no habia ocurrido cuando se
    # fijo el salario de enero de N.
    #
    # Por eso, antes de unir, se corre el año del IPC un año hacia
    # adelante: la fila que en ipc_anual dice "año 1990" (variacion de
    # precios de dic-1989 a dic-1990) pasa a juntarse con el salario del
    # "año 1991" (variacion de salario de ene-1990 a ene-1991). Sin este
    # corrimiento, se estaria comparando el ajuste de salario de enero
    # contra una inflacion que llega hasta 11-12 meses despues.
    ipc_comparable = ipc.rename(columns={"año": "año_ipc_base"})
    ipc_comparable["año"] = ipc_comparable["año_ipc_base"] + 1

    datos = salario.merge(ipc_comparable, on="año", how="inner")
    if datos.empty:
        raise ValueError(
            "No hay años en común entre las fuentes tras alinear los "
            f"periodos. Salario: {salario['año'].min()}-{salario['año'].max()}; "
            f"IPC (corrido +1 año): {ipc_comparable['año'].min()}-"
            f"{ipc_comparable['año'].max()}."
        )
    datos["variacion_salario_%"] = datos["salario_minimo"].pct_change() * 100
    datos["crecimiento_real_aprox_%"] = (
        (1 + datos["variacion_salario_%"] / 100)
        / (1 + datos["variacion_ipc_anual_%"] / 100)
        - 1
    ) * 100

    # La tabla completa (con las columnas auxiliares de trabajo, como
    # "periodo" o "año_ipc_base") se guarda en Parquet en vez de
    # imprimirse entera en consola: es un dato consultable después, no
    # algo para leer de corrida en 28 filas x 9 columnas cada vez que se
    # corre el script. La consola muestra solo el resumen de negocio.
    datos.to_parquet(RUTA_METRICAS, engine="pyarrow", index=False)
    print(f"\nTabla conectada (salario + IPC + métricas) guardada en: {RUTA_METRICAS}")

    generar_grafica(datos)

    crecimiento_real = datos["crecimiento_real_aprox_%"].dropna()
    anios_con_dato = len(crecimiento_real)
    anios_ganancia_real = (crecimiento_real > 0).sum()
    anios_perdida_real = (crecimiento_real < 0).sum()

    print("\nRESUMEN: CRECIMIENTO REAL DEL SALARIO MINIMO (vs. IPC)")
    print(
        f"Años con dato comparable: {anios_con_dato} "
        f"({datos['año'].iloc[1]}-{datos['año'].iloc[-1]})"
    )
    print(
        f"Años con ganancia real (creció por encima del IPC): {anios_ganancia_real}"
    )
    print(
        f"Años con pérdida real (el IPC le ganó): {anios_perdida_real}"
    )
    print(f"Crecimiento real promedio por año: {crecimiento_real.mean():.2f}%")
    fila_peor = datos.loc[datos["crecimiento_real_aprox_%"].idxmin()]
    fila_mejor = datos.loc[datos["crecimiento_real_aprox_%"].idxmax()]
    print(
        f"Peor año (real): {int(fila_peor['año'])} "
        f"({fila_peor['crecimiento_real_aprox_%']:.2f}%)"
    )
    print(
        f"Mejor año (real): {int(fila_mejor['año'])} "
        f"({fila_mejor['crecimiento_real_aprox_%']:.2f}%)"
    )
    print(
        "\nNota: 'crecimiento real' es una aproximación de calendario "
        "(ver README, sección Limitaciones), no un ajuste con la fecha "
        "exacta de cada resolución salarial."
    )


if __name__ == "__main__":
    main()
