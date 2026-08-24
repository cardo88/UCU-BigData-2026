# Actividad 04 - Información relevante embebida en HTML (SMN)

## Objetivo

Esta actividad extrae información del Salario Mínimo Nacional (SMN) que no
existe como archivo descargable, sino como texto y una tabla embebidos en
una página del Ministerio de Desarrollo Social (MIDES). Un LLM gratuito en
la nube la extrae y la deja almacenada para que un analista la use como
complemento de los datos ya trabajados en Actividad 2 y Actividad 3.

Se extraen dos tipos de información:

- **Contexto de negocio**: definición legal del SMN, organismo que fija el
  valor, fuente de datos original, población objetivo, unidad de medida,
  frecuencia de actualización, período cubierto declarado e institución
  publicadora.
- **La tabla de valores del SMN por año** ("Pesos corrientes", 1991-2021)
  que la página muestra de forma interactiva, y que también está presente
  como texto en el HTML estático.

## Fuente

Página de indicadores de MIDES:

[Salario Mínimo Nacional (SMN)](https://www.gub.uy/ministerio-desarrollo-social/indicador/salario-minimo-nacional-smn)

No se descarga ningún XML ni Parquet de esta página — toda la información
sale de su HTML.

## Orden de ejecución

Los comandos se ejecutan desde la raíz del repositorio, con el entorno
virtual activado:

```bash
source .venv/bin/activate
python -m pip install requests beautifulsoup4 python-dotenv pandas pyarrow
```

Se necesita una API key gratuita de [OpenRouter](https://openrouter.ai/keys):

```bash
cp Actividad04/.env.example Actividad04/.env
# completar OPENROUTER_API_KEY en Actividad04/.env
```

`Actividad04/.env` no se sube al repositorio (está en `.gitignore`).

```bash
python Actividad04/actividad04.py
```

El script genera:

```text
Actividad04/pagina_smn.html
Actividad04/info_relevante.json
Actividad04/info_relevante.parquet
Actividad04/smn_serie_html.parquet
```

## Funciones

`actividad04.py` implementa las cuatro funciones pedidas por la consigna:

- **`Ingesta_HTML(url)`**: descarga el HTML crudo de la página.
- **`Extractor_de_Info_Relevante(prompt, html)`**: limpia el HTML
  (descarta script/estilos/nav/footer con `BeautifulSoup`) y envía el texto
  resultante junto al prompt a un LLM gratuito vía OpenRouter (modelo
  `nvidia/nemotron-nano-9b-v2:free` por defecto, configurable con la
  variable de entorno `OPENROUTER_MODEL`). Reintenta con backoff si el
  proveedor gratuito responde 429 (rate-limit compartido, frecuente en
  estos modelos).
- **`Almacenar_Info_Relevante(respuesta_llm)`**: separa la respuesta del
  LLM en dos destinos — el contexto de negocio en `info_relevante.json` /
  `.parquet`, y la tabla SMN (tipada año/valor, convirtiendo el separador
  de miles uruguayo) en `smn_serie_html.parquet`.
- **`Visualiza_Info_Relevante()`**: muestra el contexto de negocio en
  consola y contrasta `smn_serie_html.parquet` contra
  `Actividad02/salario_minimo_clean.parquet` para confirmar que la serie
  extraída del HTML coincide con la fuente estructurada ya usada en
  Actividad 2 y 3.

## Punto clave

Toda la serie SMN que en Actividad 2 se obtuvo descargando y parseando un
XML de datos abiertos, en esta actividad se obtiene extrayéndola del HTML
de una página con un LLM — y el resultado coincide con la fuente
estructurada. No hizo falta ningún archivo descargable: la información
estaba embebida en la página, tal como plantea la consigna.

## Limitaciones

- Los modelos gratuitos de OpenRouter comparten un pool con rate-limit del
  proveedor upstream; su disponibilidad cambia con el tiempo y a veces
  responden 429 sin que sea un error del pipeline.
- La tabla SMN se pasa al LLM como texto plano (`get_text()` del HTML), con
  la fila de años y la fila de valores como dos listas consecutivas que el
  modelo alinea por posición — no es un parseo determinístico de la
  etiqueta `<table>`. Para esta página se validó contra Actividad 2 y
  coincide, pero con tablas más grandes o irregulares convendría parsear
  el HTML directamente en Python.
- La extracción depende de que la página conserve su estructura actual.

## Informe

El informe completo, con resultados y la respuesta a si esta información
es necesaria para las métricas ya calculadas, está en
[Actividad04.md](Actividad04.md).
