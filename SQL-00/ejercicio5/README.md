# SQL-00 - Ejercicio 5

Análisis de la metadata de los datasets públicos de IMDb y reflexión sobre
cómo modelarlos, usando los conceptos de la materia: índices (qué conviene
indexar) e índices hash, modelo transaccional vs. analítico, decisiones
estructurales (particionamiento, granularidad, índices, esquema,
disponibilidad, escalabilidad, rendimiento de consultas), modelado
independiente del punto de vista y visualización.

> Ejercicio conceptual: no hay consultas SQL. El entregable es este análisis.

## 1. La fuente

Página: <https://datasets.imdbws.com/>

Archivos `.tsv.gz` (TSV + `gzip`), **refrescados a diario**, para uso personal
y no comercial. Descripción oficial de campos:
<https://developer.imdb.com/non-commercial-datasets/>.

La página publica 7 archivos. En `SQL-00/imdbws/` se descargaron 3:

| Archivo | Descargado | Filas (aprox.) | Una fila representa… |
| --- | --- | --- | --- |
| `name.basics.tsv.gz` | ✅ | 15.6 M | una persona |
| `title.basics.tsv.gz` | ✅ | 12.8 M | un título |
| `title.ratings.tsv.gz` | ✅ | 1.7 M | un título (puntaje **ya agregado**) |
| `title.akas.tsv.gz` | ❌ | — | un título × región/idioma |
| `title.crew.tsv.gz` | ❌ | — | un título (directores/guionistas) |
| `title.episode.tsv.gz` | ❌ | — | un episodio |
| `title.principals.tsv.gz` | ❌ | — | un título × persona × rol |

Con los 3 archivos se puede responder sobre títulos, su puntaje y personas.
**No** se puede saber quién actuó/dirigió cada título, ni los títulos
alternativos por país, ni la relación temporada/episodio, hasta sumar los
otros archivos.

## 2. Metadata de los datasets descargados

### 2.1 `title.basics` — un registro por título

| Columna | Tipo lógico | Notas |
| --- | --- | --- |
| `tconst` | texto | **Clave**. `tt` + dígitos. |
| `titleType` | categórico | `movie`, `short`, `tvEpisode`, `tvSeries`, `video`, `videoGame`, … (11 valores; apareció un `tvPilot` con **1** fila). |
| `primaryTitle` / `originalTitle` | texto | Título de difusión / original. |
| `isAdult` | booleano | `0` / `1`. |
| `startYear` / `endYear` | entero (año) | `endYear` solo aplica a series; `\N` frecuente. |
| `runtimeMinutes` | entero | `\N` frecuente. |
| `genres` | **lista** | Hasta 3, separados por coma. `\N` si falta. |

Distribución de `titleType` (12.8 M filas): `tvEpisode` 9.87 M, `short`
1.16 M, `movie` 0.76 M, `video` 0.33 M, `tvSeries` 0.30 M, … La mayoría de las
filas **no** son películas.

### 2.2 `title.ratings` — un registro por título calificado

| Columna | Tipo lógico | Notas |
| --- | --- | --- |
| `tconst` | texto | **Clave** + referencia a `title.basics`. |
| `averageRating` | decimal (1 decimal) | 1.0–10.0. **Promedio ya calculado**, no el voto individual. |
| `numVotes` | entero | Cantidad de votos. |

Solo ~13 % de los títulos tiene rating. Un título tiene como mucho una fila de
rating, y muchísimos no tienen ninguna.

### 2.3 `name.basics` — un registro por persona

| Columna | Tipo lógico | Notas |
| --- | --- | --- |
| `nconst` | texto | **Clave**. `nm` + dígitos. |
| `primaryName` | texto | |
| `birthYear` / `deathYear` | entero (año) | `\N` en la mayoría (~70 % sin `birthYear` en una muestra). |
| `primaryProfession` | **lista** | `actor,miscellaneous,producer`. |
| `knownForTitles` | **lista de referencias** | Hasta 4 `tconst`. |

### 2.4 Convenciones comunes

- Separador: tabulador. Encoding: UTF-8. Nulo: la cadena literal `\N`.
- Identificadores estables: `tconst` (`tt…`), `nconst` (`nm…`) → sirven como
  **clave natural**.
- Campos multivaluados por coma: `genres`, `primaryProfession`,
  `knownForTitles`.
- Todo llega como texto: años, enteros y decimales se convierten en la
  ingesta.

## 3. Modelado independiente del punto de vista

Primero conviene fijar el **modelo conceptual**: qué entidades hay, cómo se
identifican y cómo se relacionan. Esto no cambia según quién use los datos.

### Entidades y claves

- **Título** — clave natural `tconst`.
- **Persona** — clave natural `nconst`.
- **Puntaje** — dato del título (0 o 1 por título), clave `tconst`.
- **Género** y **Profesión** — catálogos (listas de valores fijas y cortas).

### Relaciones

- Título — Puntaje: 1 a 0/1.
- Título — Género: muchos a muchos (campo `genres`).
- Persona — Profesión: muchos a muchos (`primaryProfession`).
- Persona — Título "conocida por": muchos a muchos (`knownForTitles`).
- *(con los archivos que faltan)* Persona — Título "participó en"
  (`principals`) y Título → episodio (`episode`).

### Granularidad (qué representa una fila) — decisión importante

| Concepto | Grano disponible | Comentario |
| --- | --- | --- |
| Título | el título | Fino. Serie y episodio son filas distintas. |
| Puntaje | el título | **Ya viene resumido**: promedio + cantidad de votos. El voto de cada usuario **no está** → ese detalle no se puede recuperar con estos archivos. |
| Persona | la persona | Fino. |
| Participación | título × persona × rol | Solo con `principals` (no descargado). |

Consecuencia: no se puede analizar "cómo cambió el rating en el tiempo" ni
"votos por usuario"; con estos datos solo hay una foto del promedio actual.
Para tener historia habría que **guardar una copia por día** del archivo
(grano = título × día).

Este modelo conceptual (entidades + claves + relaciones + grano) es el punto
de partida común. Lo que sigue (índices, particiones, esquema físico) **sí**
depende de para qué se van a usar los datos.

## 4. Modelo transaccional vs. analítico

| | Transaccional | Analítico |
| --- | --- | --- |
| Uso | Muchas altas/bajas/modificaciones chicas; se lee de a un registro | Se carga en bloque y se consulta para **agrupar y resumir** millones de filas |
| Esquema | Muy normalizado, sin datos repetidos | Se acepta repetir/desnormalizar para consultar más fácil |
| Ejemplo | La base real de IMDb (alguien carga un título, alguien vota) | **Este caso**: un archivo completo que se reemplaza cada día y se explota para reportes |

**Los datasets de IMDb son un caso analítico**: no hay transacciones para
aplicar, es un volcado que se rehace entero cada día y se consulta para sacar
totales, promedios y rankings. Eso orienta las decisiones de abajo.

## 5. Decisiones estructurales

### 5.1 Modelado de datos (esquema)

- **Modelo normalizado** (punto de partida neutro): tablas `title`, `name`,
  `title_rating`, más `genre` + `title_genre`, `profession` +
  `name_profession`, `name_known_for`. Evita repetir datos y mantiene la
  integridad.
- **Modelo para análisis**: una tabla central de "hechos" con las medidas
  (`average_rating`, `num_votes`) y tablas de "dimensiones" alrededor
  (título, persona, género, año). Pensado para reportes.
- **Vista/tabla ancha**: título + puntaje + géneros ya combinados en una sola
  tabla, para que una herramienta de visualización no tenga que cruzar varias
  tablas.

### 5.2 ¿Qué conviene indexar?

Un índice acelera buscar o filtrar por una columna, a cambio de ocupar
espacio y de encarecer un poco las escrituras. Acá las escrituras son una
carga masiva por día, así que el costo de mantenerlos casi no importa: se
puede **cargar primero y crear los índices después**.

Conviene indexar las columnas por las que **se busca, se filtra o se cruza**:

| Índice sobre… | Para qué |
| --- | --- |
| `title(tconst)`, `name(nconst)` (claves) | Buscar un título/persona puntual y cruzar tablas entre sí. |
| `title_rating(tconst)` | Unir cada título con su puntaje. |
| `title(titleType)` | Filtrar "solo películas", "solo series". |
| `title(startYear)` | Filtrar por año o rango de años ("estrenos de 2020-2025"). |
| `title_rating(numVotes)` y `title_rating(averageRating)` | Rankear ("top por votos", "mejor puntuadas"). |
| `title_genre(genre_id)` | "Todos los títulos de un género". |

No conviene indexar columnas que casi no se usan para filtrar (`isAdult`,
`endYear`) ni las de texto largo y libre (`primaryTitle`) salvo que haga
falta búsqueda por texto, que es otro tipo de índice.

Nota sobre `genres`: mientras esté como lista `"Animation,Comedy,Romance"` en
una sola celda, no se puede indexar de forma útil (hay que hacer
`LIKE '%Comedy%'`, que recorre todo). Si se separa a la tabla `title_genre`,
un índice sobre el género resuelve la consulta al instante.

### 5.3 Índices hash

Un índice **hash** está pensado para búsquedas por **valor exacto** (`campo =
valor`). Es rápido para eso, pero **no** sirve para rangos (`>`, `<`,
`BETWEEN`) ni para ordenar.

En estos datos el uso natural sería buscar por `tconst` o `nconst` exactos
(por ejemplo, traer la ficha de una persona a partir de su `nconst`). Aun así,
el índice normal de la clave ya resuelve esa búsqueda por igualdad **y**
además sirve para rangos y para ordenar, así que en general alcanza con ese.
El índice hash tendría sentido si hubiera muchísimas búsquedas por id exacto y
nunca por rango.

### 5.4 Particionamiento

Partir una tabla grande en pedazos según el valor de una columna, para que
cada consulta lea solo el pedazo que necesita.

- **Por `titleType`**: separa `tvEpisode` (77 % de las filas) del resto; una
  consulta de películas nunca toca los episodios.
- **Por año de estreno**: "estrenos de la última década" lee solo 1–2
  particiones.
- En las tablas de relación grandes (`title_principals`, cuando se sume),
  partir por `tconst` reparte el volumen.

Además de acelerar consultas, ayuda con la carga diaria: se puede cargar la
tanda nueva en una partición aparte y engancharla, en vez de reescribir toda
la tabla.

### 5.5 Disponibilidad

El dato se regenera **todos los días**. Para no cortar el servicio mientras se
recarga:

- Cargar la versión nueva en tablas aparte, validar y recién ahí cambiarles el
  nombre (reemplazo casi instantáneo).
- O cargar y "enganchar" la partición del día.
- Si hay varios consumidores a la vez (visualización, notebooks), agregar
  copias de solo lectura de la base.

### 5.6 Escalabilidad

- Volumen: 12.8 M títulos, 15.6 M personas, y `principals` del orden de
  decenas de millones. Entra en un solo servidor bien dimensionado.
- Primero crecer **hacia arriba** (más memoria para que las consultas grandes
  no vayan tanto a disco).
- Para la parte de análisis, guardar los datos en formato **columnar**
  (por ejemplo Parquet, o un motor orientado a columnas): comprime mucho
  porque los ids y textos se repiten, y los promedios/conteos por columna
  salen más rápido.
- Repartir la base en varias máquinas recién si el volumen o la cantidad de
  usuarios lo exige. Con este tamaño todavía no hace falta.

### 5.7 Rendimiento de consultas

- Combinar **particiones + índices** en las columnas de filtro habituales
  (tipo, año, puntaje).
- **Pre-calcular** los resúmenes que se piden seguido (títulos por género y
  año, puntaje promedio por género) en tablas o vistas que se actualizan una
  vez por día, junto con la carga.
- Separar `genres` a su propia tabla para cambiar un `LIKE` lento por un
  cruce indexado.
- Usar tipos adecuados (año como entero chico, puntaje con un decimal) para
  que cada fila ocupe menos y los recorridos sean más rápidos.

## 6. Las decisiones cambian según el rol

| Rol | Qué prioriza | Decisiones típicas |
| --- | --- | --- |
| **Analista / negocio** | Responder rápido y sin ambigüedad | Modelo para análisis o tabla ancha; `genre` como tabla; resúmenes ya calculados. No le importa el costo de los índices. |
| **Ingeniero de datos** | Carga diaria confiable | Convertir `\N` a nulo, tipar, orden de carga, estrategia de reemplazo, particiones para abaratar la recarga. |
| **DBA / administrador** | Espacio y velocidad | Elegir qué indexar (claves, `titleType`, `startYear`, `numVotes`), particionar por tipo/año, tipos chicos. |
| **Científico de datos** | Datos completos, incluso "sucios" | Conservar nulos y filas dudosas; formato columnar; quiere `numVotes` para ponderar y `principals` para análisis de redes. |
| **Modelador / arquitecto** | Integridad y claridad | Modelo normalizado con catálogos de `genre`/`profession`; deja el modelo de análisis como capa derivada. |

El mismo dataset lleva a un esquema muy normalizado (modelador) o muy plano y
pre-resumido (analista, visualización). El diseño final es un punto medio.

## 7. Visualización

- **Preguntas que se pueden graficar**: distribución de puntajes; cantidad de
  títulos por año y por tipo; evolución de los géneros en el tiempo; top de
  títulos por cantidad de votos; duración media por tipo/década; (con
  `principals`) filmografías y colaboraciones actor–director.
- **Qué necesita el modelo para que un tablero responda rápido**:
  - una capa **ya combinada** (tabla/vista ancha) para no cruzar 5 tablas por
    gráfico;
  - los resúmenes **pre-calculados** al nivel del tablero (por ejemplo género
    × año), porque recalcular sobre 12 M de filas en cada clic no escala;
  - una tabla de fechas/años para los ejes de tiempo;
  - que los filtros del tablero (tipo, año, género) coincidan con las columnas
    por las que se particionó e indexó.
- **Cuidados propios de estos datos**: filtrar por un mínimo de votos antes de
  rankear por puntaje (si no, títulos con 5 votos y 10.0 encabezan todo);
  `tvEpisode` domina los conteos y aplasta al resto si no se separa; los años
  vacíos o futuros distorsionan las series de tiempo.

## 8. Dudas que aparecen y obligan a mirar los datos

1. **¿`genres` tiene siempre ≤ 3 valores?** Verificar el máximo real.
2. **¿`knownForTitles` apunta a títulos presentes en el recorte?** Con solo 3
   archivos, probablemente no → decidir qué hacer con esas referencias sueltas.
3. **¿`tconst` / `nconst` son únicos en cada archivo?** Confirmar antes de
   usarlos como clave.
4. **¿Qué significa que un título no esté en `title.ratings`?** ¿Sin votos o
   sin estreno? Cambia cómo se leen los promedios y los faltantes.
5. **`startYear` / `endYear`**: ¿años futuros? ¿`endYear` menor que
   `startYear`? ¿valores no numéricos además de `\N`?
6. **`runtimeMinutes`**: ¿valores absurdos (0, negativos, miles de minutos)?
7. **`primaryProfession` vacío**: ¿cuántas personas sin profesión y qué hacer
   con ellas?
8. **`titleType`**: la lista de valores sale de los datos, no de la doc; ¿el
   `tvPilot` con 1 sola fila es válido o un error?
9. **Parseo**: ¿algún título trae tabuladores o un `\N` literal que rompa el
   TSV?
10. **Tamaño de `principals`** (cuando se descargue): define si hace falta
    particionar o pasar a columnar.

Conclusión: la metadata alcanza para fijar el **modelo conceptual**
(entidades, claves, relaciones, grano) sin depender de para qué se use. Las
decisiones **físicas** —qué indexar, cómo particionar, qué resúmenes
pre-calcular para visualización— dependen de que este es un caso **analítico**
(archivo diario, consultas que agrupan), y varias necesitan **perfilar los
datos reales** primero, como en los ejercicios de ingesta y profiling de las
Actividades anteriores.
