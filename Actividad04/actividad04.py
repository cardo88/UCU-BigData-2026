# =============================================================================
# ACTIVIDAD 4 - INFORMACION RELEVANTE EMBEBIDA EN HTML (SMN)
# =============================================================================
#
# La pagina de MIDES sobre el Salario Minimo Nacional (SMN) trae, en texto
# libre dentro del HTML, informacion que no existe en el XML/parquet usado en
# Actividad02/03 (definicion legal, organismo que fija el valor, poblacion
# objetivo, fuente original, periodo cubierto). Este script la extrae con un
# LLM gratuito (via OpenRouter) y la deja disponible para un analista.
#
# Funciones pedidas por la consigna:
#   Ingesta_HTML                  -> descarga el HTML crudo
#   Extractor_de_Info_Relevante   -> prompt + html -> respuesta del LLM (insight)
#   Almacenar_Info_Relevante      -> persiste la respuesta (JSON + Parquet)
#   Visualiza_Info_Relevante      -> muestra la info relevante almacenada
#
# Como ejecutar, desde la raiz del repositorio y con el venv activado:
#   python -m pip install requests beautifulsoup4 python-dotenv pandas pyarrow
#   cp Actividad04/.env.example Actividad04/.env   # completar OPENROUTER_API_KEY
#   python Actividad04/actividad04.py
# =============================================================================

import json
import os
import re
import time
from pathlib import Path
from typing import Optional

import pandas as pd
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

URL_SMN = "https://www.gub.uy/ministerio-desarrollo-social/indicador/salario-minimo-nacional-smn"
RUTA_HTML_RAW = Path("Actividad04/pagina_smn.html")
RUTA_INFO_JSON = Path("Actividad04/info_relevante.json")
RUTA_INFO_PARQUET = Path("Actividad04/info_relevante.parquet")
RUTA_SERIE_PARQUET = Path("Actividad04/smn_serie_html.parquet")
RUTA_SMN_CLEAN = Path("Actividad02/salario_minimo_clean.parquet")

CLAVE_SERIE = "serie_smn_tabla"

# Modelo gratuito de OpenRouter. La lista de modelos ":free" cambia con el
# tiempo; si este deja de estar disponible, se puede pisar con la variable de
# entorno OPENROUTER_MODEL o cambiar el default aca.
OPENROUTER_MODEL_DEFAULT = "nvidia/nemotron-nano-9b-v2:free"


def Ingesta_HTML(url: str = URL_SMN, ruta_destino: Path = RUTA_HTML_RAW) -> str:
    """Descarga el HTML crudo de la pagina y lo guarda en disco."""
    respuesta = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    respuesta.raise_for_status()

    ruta_destino.parent.mkdir(parents=True, exist_ok=True)
    ruta_destino.write_text(respuesta.text, encoding="utf-8")
    return respuesta.text


def _texto_legible(html: str) -> str:
    """Reduce el HTML a texto plano, descartando script/estilos/nav/footer."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "header", "footer", "svg", "noscript"]):
        tag.decompose()

    texto = soup.get_text("\n")
    lineas = [linea.strip() for linea in texto.splitlines() if linea.strip()]
    return "\n".join(lineas)


def Extractor_de_Info_Relevante(prompt: str, html: str) -> str:
    """
    Recibe un prompt (que se quiere extraer) y el HTML crudo de la pagina.
    Llama a un LLM gratuito en la nube (OpenRouter) y devuelve su respuesta.
    """
    load_dotenv(Path("Actividad04/.env"))
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Falta OPENROUTER_API_KEY. Crear Actividad04/.env a partir de "
            "Actividad04/.env.example con la key de https://openrouter.ai/keys"
        )

    modelo = os.environ.get("OPENROUTER_MODEL", OPENROUTER_MODEL_DEFAULT)
    texto_pagina = _texto_legible(html)[:15000]  # recorte defensivo de tokens

    payload = {
        "model": modelo,
        "temperature": 0,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Extraes informacion relevante de paginas HTML de "
                    "organismos publicos uruguayos. Respondes UNICAMENTE "
                    "con JSON valido, sin texto adicional ni markdown."
                ),
            },
            {
                "role": "user",
                "content": f"{prompt}\n\nTexto de la pagina:\n\n{texto_pagina}",
            },
        ],
    }

    # los modelos ":free" de OpenRouter comparten un pool con rate-limit
    # propio del proveedor upstream; un 429 esporadico no es un error del
    # pipeline, asi que reintentamos con backoff antes de fallar.
    intentos = 4
    for intento in range(1, intentos + 1):
        respuesta = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=60,
        )
        if respuesta.status_code != 429 or intento == intentos:
            respuesta.raise_for_status()
            return respuesta.json()["choices"][0]["message"]["content"]
        time.sleep(5 * intento)


def _numero_uruguayo(valor) -> Optional[float]:
    """Convierte '17.930' (formato uruguayo, punto de miles) a 17930.0."""
    if valor is None:
        return None
    texto = re.sub(r"[^0-9.,\-]", "", str(valor))
    if not texto:
        return None
    texto = texto.replace(".", "").replace(",", ".")
    try:
        return float(texto)
    except ValueError:
        return None


def Almacenar_Info_Relevante(
    respuesta_llm: str,
    ruta_json: Path = RUTA_INFO_JSON,
    ruta_parquet: Path = RUTA_INFO_PARQUET,
    ruta_serie_parquet: Path = RUTA_SERIE_PARQUET,
) -> dict:
    """
    Parsea la respuesta JSON del LLM y la persiste.

    La respuesta trae dos tipos de informacion, que se guardan por separado:
    - metadata descriptiva (definicion legal, organismo, etc.) -> JSON + Parquet.
    - la tabla de valores SMN por anio embebida en el HTML (clave
      `serie_smn_tabla`), si el prompt la pidio -> Parquet aparte, tipado como
      anio (int) / valor (float), lista para conectar con
      Actividad02/salario_minimo_clean.parquet.
    """
    texto = respuesta_llm.strip()
    texto = re.sub(r"^```(json)?|```$", "", texto, flags=re.MULTILINE).strip()
    info = json.loads(texto)

    serie = info.pop(CLAVE_SERIE, None)

    ruta_json.parent.mkdir(parents=True, exist_ok=True)
    ruta_json.write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    pd.json_normalize(info).to_parquet(ruta_parquet, index=False)

    if serie:
        df_serie = pd.DataFrame(serie)
        df_serie["anio"] = df_serie["anio"].apply(lambda v: int(_numero_uruguayo(v)))
        df_serie["valor"] = df_serie["valor_pesos_corrientes"].apply(_numero_uruguayo)
        df_serie = df_serie[["anio", "valor"]].sort_values("anio").reset_index(drop=True)
        df_serie.to_parquet(ruta_serie_parquet, index=False)

    return info


def Visualiza_Info_Relevante(
    ruta_json: Path = RUTA_INFO_JSON,
    ruta_serie_parquet: Path = RUTA_SERIE_PARQUET,
    ruta_smn_clean: Path = RUTA_SMN_CLEAN,
) -> dict:
    """Muestra en consola la informacion relevante almacenada."""
    info = json.loads(ruta_json.read_text(encoding="utf-8"))

    print("=" * 78)
    print("INFORMACION RELEVANTE EXTRAIDA - Salario Minimo Nacional (gub.uy/MIDES)")
    print("=" * 78)
    for clave, valor in info.items():
        etiqueta = clave.replace("_", " ").capitalize()
        print(f"- {etiqueta}: {valor}")
    print("=" * 78)

    if ruta_serie_parquet.exists():
        df_html = pd.read_parquet(ruta_serie_parquet)
        print(f"\nTabla SMN embebida en el HTML: {len(df_html)} anios "
              f"({df_html['anio'].min()}-{df_html['anio'].max()})")

        if ruta_smn_clean.exists():
            df_actual = pd.read_parquet(ruta_smn_clean)
            comunes = df_html.merge(
                df_actual, left_on="anio", right_on="año", suffixes=("_html", "_parquet")
            )
            coinciden = (comunes["valor_html"] == comunes["valor_parquet"]).all()
            print(f"- Contraste con Actividad02/salario_minimo_clean.parquet "
                  f"({len(comunes)} anios en comun): "
                  f"{'coinciden' if coinciden else 'HAY DIFERENCIAS'} en el valor. "
                  f"Esta serie se obtuvo del HTML, sin descargar el archivo "
                  f"estructurado (XML/parquet).")
        print("=" * 78)

    return info


PROMPT_SMN = (
    "De esta pagina del Ministerio de Desarrollo Social (MIDES) sobre el "
    "indicador Salario Minimo Nacional (SMN), devolve un UNICO objeto JSON "
    "PLANO (todas las claves siguientes al nivel raiz del JSON, ninguna "
    "anidada bajo una clave contenedora como 'contexto' o 'datos') con "
    "exactamente estas 9 claves:\n"
    "definicion_legal, organismo_que_fija_el_valor, fuente_de_datos_original, "
    "poblacion_objetivo, unidad_de_medida, frecuencia_de_actualizacion, "
    "periodo_cubierto, institucion_publicadora: informacion de contexto que "
    "complementa un analisis de datos del SMN y que NO es la serie numerica. "
    "Si un dato no aparece en la pagina, usa null en esa clave.\n"
    "serie_smn_tabla: la tabla de datos del SMN por anio que aparece en la "
    "pagina (fila 'Pesos corrientes' con un valor por cada anio de la "
    "cabecera), como una lista de objetos {\"anio\": ..., "
    "\"valor_pesos_corrientes\": ...} con TODOS los anios y valores de esa "
    "tabla, copiados literalmente como aparecen en el texto (no hagas "
    "calculos ni conversiones vos mismo).\n"
    "Ejemplo de la forma exacta esperada (con datos de relleno, no los "
    "copies): {\"definicion_legal\": \"...\", \"organismo_que_fija_el_valor\": "
    "\"...\", \"serie_smn_tabla\": [{\"anio\": \"1991\", "
    "\"valor_pesos_corrientes\": \"118\"}, ...]}"
)


if __name__ == "__main__":
    html = Ingesta_HTML()
    respuesta_llm = Extractor_de_Info_Relevante(PROMPT_SMN, html)
    Almacenar_Info_Relevante(respuesta_llm)
    Visualiza_Info_Relevante()
