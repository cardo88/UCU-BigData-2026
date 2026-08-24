# Actividad 04 - Información Relevante Embebida en HTML (SMN)

Repositorio: <https://github.com/cardo88/UCU-BigData-2026.git>

## Objetivo

El Salario Mínimo Nacional (SMN) trabajado en Actividad02/03 se tomó de un
XML/Parquet estructurado que solo trae **año** y **valor**. La definición
legal del SMN, quién lo fija, a quién aplica y su período de cobertura
declarado no existen en ese archivo: están como texto libre en la página de
indicadores de MIDES. El objetivo de esta actividad es extraer esa
información no estructurada con un LLM, dejarla almacenada para que un
analista la use como contexto, y evaluar si es necesaria para las métricas
ya calculadas.

Fuente HTML: [Salario Mínimo Nacional (SMN) — MIDES](https://www.gub.uy/ministerio-desarrollo-social/indicador/salario-minimo-nacional-smn)

## Arquitectura implementada

`actividad04.py` implementa las cuatro funciones pedidas por la consigna.
El prompt le pide al LLM dos cosas en un mismo JSON:

1. **Contexto de negocio** (definición legal, organismo que fija el valor,
   fuente original, población objetivo, unidad, frecuencia, período
   cubierto declarado, institución publicadora) — no está en ningún
   archivo estructurado usado hasta ahora.
2. **La tabla de valores SMN por año** que la página muestra de forma
   interactiva (fila "Pesos corrientes" x 31 columnas de año). Esta tabla
   *sí* está en el HTML estático que descarga `Ingesta_HTML` — no requiere
   JavaScript ni una API aparte — pero como es una tabla embebida en el
   diseño de la página (no un archivo de datos publicado), cuenta como la
   misma clase de "información no estructurada" que plantea la consigna.

- **`Ingesta_HTML(url)`**: descarga el HTML crudo de la página y lo guarda
  en `pagina_smn.html`.
- **`Extractor_de_Info_Relevante(prompt, html)`**: recibe el prompt de
  negocio y el HTML sin estructurar; limpia el HTML (descarta
  script/estilos/nav/footer con `BeautifulSoup`, reduce la página a ~2.2K
  caracteres de texto plano) y lo envía junto al prompt a un LLM gratuito
  en la nube vía [OpenRouter](https://openrouter.ai) (modelo
  `nvidia/nemotron-nano-9b-v2:free`, configurable por variable de entorno
  `OPENROUTER_MODEL`). Devuelve la respuesta del modelo (el *insight*) como
  texto JSON.
- **`Almacenar_Info_Relevante(respuesta_llm)`**: separa la respuesta en dos
  destinos. El contexto de negocio va a `info_relevante.json` (legible,
  para el analista) e `info_relevante.parquet`. La tabla SMN
  (`serie_smn_tabla`) se tipa (año → int, valor → float, convirtiendo el
  separador de miles uruguayo "17.930" → 17930.0) y se guarda aparte en
  `smn_serie_html.parquet`, en el mismo formato long (`año`, `valor`) que
  `Actividad02/salario_minimo_clean.parquet`, para poder conectarla
  directamente.
- **`Visualiza_Info_Relevante()`**: muestra el contexto de negocio y,
  además, compara automáticamente `smn_serie_html.parquet` contra
  `Actividad02/salario_minimo_clean.parquet`: cuántos años se solapan, si
  coinciden en valor, y qué años nuevos aporta el HTML.

```bash
source .venv/bin/activate
python -m pip install requests beautifulsoup4 python-dotenv pandas pyarrow
cp Actividad04/.env.example Actividad04/.env   # completar OPENROUTER_API_KEY
python Actividad04/actividad04.py
```

La API key de OpenRouter (gratuita, [openrouter.ai/keys](https://openrouter.ai/keys))
se lee de `Actividad04/.env`, que está excluido de git — nunca queda
en el repositorio.

**Nota sobre modelos gratuitos**: los modelos `:free` de OpenRouter
comparten un pool con rate-limit del proveedor upstream (Google AI Studio,
etc.) y su disponibilidad cambia con frecuencia — durante las pruebas,
`meta-llama/llama-3.1-8b-instruct:free` ya no existía como variante
gratuita, y otros dos modelos gratuitos devolvieron 429 antes de encontrar
uno disponible. Por eso `Extractor_de_Info_Relevante` reintenta con backoff
ante un 429 antes de fallar.

## Resultados

**Contexto de negocio** — el LLM devolvió, entre otros datos:

- **Definición legal**: según la Ley 10449 y el Decreto 1534/969, el SMN es
  el "piso por debajo del cual no puede estar ninguna remuneración".
- **Organismo que fija el valor**: Ministerio de Trabajo y Seguridad Social
  (la página está publicada por MIDES, pero quien fija el valor es otro
  organismo).
- **Población objetivo**: personas mayores de 18 años.
- **Período cubierto declarado en la página**: 1991-2021.

**Tabla SMN embebida** — el LLM extrajo los 31 pares año/valor de la tabla
"Pesos corrientes" de la página (1991 a 2021), sin necesidad de descargar
ningún XML ni Parquet: la fuente fue directamente el HTML de la página. Al
conectar esa tabla automáticamente contra
`Actividad02/salario_minimo_clean.parquet` desde `Visualiza_Info_Relevante`,
los años en común coinciden exactamente en valor con el archivo estructurado
ya usado en Actividad02/03 — es decir, la extracción vía LLM sobre HTML
reprodujo correctamente la misma serie que hasta ahora sólo se obtenía
descargando el archivo de datos abiertos.

## ¿Es necesaria esta información para las métricas ya calculadas?

**El contexto de negocio (definición legal, organismo, población
objetivo): no cambia ningún cálculo.** Las métricas de Actividad02
(mínimo, máximo, promedio del SMN) y Actividad03 (variación anual,
crecimiento real vs. IPC) usan solo la serie numérica año→valor; esos
campos son metadata que ayuda a interpretar el indicador (a quién aplica,
con qué respaldo legal), pero no son un input de las fórmulas.

**El punto relevante de esta actividad no es si la tabla tenía más o menos
años que el archivo estructurado, sino que no hizo falta descargar el
archivo estructurado en absoluto.** Toda la serie SMN que en Actividad02 se
obtuvo bajando y parseando un XML de datos abiertos, acá se obtuvo
extrayéndola del HTML de la página con el LLM, y el resultado coincide con
la fuente estructurada. Eso es exactamente lo que plantea la consigna: hay
información que un analista necesita y que no está disponible como archivo
descargable, sino embebida en una página — y este pipeline (`Ingesta_HTML`
→ `Extractor_de_Info_Relevante` → `Almacenar_Info_Relevante`) demuestra que
se la puede dejar disponible igual, sin depender de que el organismo
publique un dataset aparte.

## Limitaciones

- El LLM gratuito puede variar su redacción entre corridas (aunque se usa
  `temperature=0`) y su disponibilidad/modelo puede cambiar sin aviso al
  ser un tier gratuito compartido. Además, en la primera versión del
  prompt el modelo devolvió los campos de contexto anidados bajo una clave
  extra en vez del JSON plano pedido; hubo que reforzar el prompt con un
  ejemplo explícito de la forma esperada.
- La tabla SMN se le pasa al LLM como texto plano (`get_text()` del HTML),
  donde la fila de años y la fila de valores quedan como dos listas
  consecutivas que el modelo tiene que alinear por posición — no es un
  parseo determinístico de la etiqueta `<table>`. Para esta página funcionó
  bien (se validó contra Actividad02, ver Resultados), pero con tablas más
  grandes o irregulares convendría parsear el HTML de la tabla
  directamente en Python en lugar de delegarlo al LLM.
- La extracción depende de que la página conserve su estructura actual; un
  cambio de diseño en gub.uy podría requerir ajustar el prompt.
- No se valida automáticamente la veracidad de lo que devuelve el LLM
  contra el HTML fuente — para esta entrega se revisó manualmente que la
  respuesta coincidiera con el contenido real de la página.

## Uso de IA como apoyo

Se utilizó asistencia de IA (Claude, Anthropic) para el diseño del pipeline,
la redacción de este documento y como apoyo en la sintaxis del código. La
elección de la fuente HTML, el prompt de extracción, la detección del
desfasaje 2018 vs. 2021 y la conclusión sobre necesidad de la información
para las métricas son criterio propio.

---

## Anexo

### A. Archivos generados

- `pagina_smn.html`: HTML crudo descargado por `Ingesta_HTML`.
- `info_relevante.json` / `info_relevante.parquet`: contexto de negocio,
  salida de `Almacenar_Info_Relevante`.
- `smn_serie_html.parquet`: tabla año/valor del SMN extraída del HTML
  (1991-2021), en el mismo formato que
  `Actividad02/salario_minimo_clean.parquet`.

### B. Código completo del script

- <https://github.com/cardo88/UCU-BigData-2026/blob/main/Actividad04/actividad04.py>

### C. Fuente del HTML

Ministerio de Desarrollo Social (MIDES) — Indicador Salario Mínimo Nacional
(SMN):
<https://www.gub.uy/ministerio-desarrollo-social/indicador/salario-minimo-nacional-smn>
