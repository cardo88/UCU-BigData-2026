# Actividad 00 - Práctica de Listas y Diccionarios (Python)

Repositorio: <https://github.com/cardo88/UCU-BigData-2026.git>

Práctica introductoria de Python enfocada en las estructuras de datos base
que después se usan todo el curso para trabajar con datos: **listas**,
**diccionarios** y **estructuras anidadas** (listas de diccionarios,
diccionarios con listas adentro, etc.).

## Objetivo

Repasar cómo Python maneja tipos de datos dentro de listas y diccionarios,
cómo se accede a sus elementos (por índice vs. por clave), y qué pasa cuando
se combinan ambas estructuras — que es exactamente la forma en la que suelen
venir los datos "crudos" (JSON, registros, filas de una tabla) antes de
pasarlos a pandas o a cualquier otra herramienta de análisis.

## Cómo correr esto

```bash
python3 Actividad00/practica_listas_diccionarios.py
```

El script no depende de ningún archivo externo ni requiere librerías más
allá de la biblioteca estándar de Python.

## Estructura del script

El archivo [`practica_listas_diccionarios.py`](practica_listas_diccionarios.py)
está organizado en 3 bloques, con 9 ejercicios en total. Cada ejercicio
imprime en consola tanto el resultado pedido como las respuestas a las
preguntas conceptuales planteadas en la consigna.

| Bloque | Ejercicios | Tema |
|---|---|---|
| 1 - Listas | 1-3 | Creación de listas, tipos de datos, acceso por índice (positivo, negativo y fuera de rango) |
| 2 - Diccionarios | 4-6 | Creación de diccionarios, acceso por clave, diccionarios con valores heterogéneos |
| 3 - Estructuras anidadas | 7-9 | Listas de diccionarios, diccionarios con listas adentro, estructuras mixtas más realistas |

## Resumen de los ejercicios

### Bloque 1 — Listas

- **Ejercicio 1**: lista `edades = [18, 21, 25, 30, 35]`. Python infiere el
  tipo `list`, cuyos elementos son `int`. El acceso es por índice, empezando
  en `0`.
- **Ejercicio 2**: lista heterogénea `datos = ["Ana", 25, 1.72, True]`. Una
  lista de Python puede mezclar tipos sin problema (`str`, `int`, `float`,
  `bool`) — la lista en sí es siempre de tipo `list`, más allá de lo que
  contenga.
- **Ejercicio 3**: acceso por índice positivo, negativo (`ciudades[-1]` para
  el último elemento) y el caso de error al acceder a un índice fuera de
  rango (`ciudades[5]` sobre una lista de 5 elementos, índices `0` a `4`),
  que lanza `IndexError: list index out of range`.

### Bloque 2 — Diccionarios

- **Ejercicio 4**: diccionario `persona` con claves `nombre`, `edad`,
  `altura`, `estudiante`. A diferencia de una lista, acá los valores se
  acceden por **clave**, no por posición.
- **Ejercicio 5**: acceso por clave (`persona['nombre']`, etc.). La
  diferencia clave con las listas: `ciudades[2]` depende de la posición del
  elemento, `persona['edad']` depende del nombre de la clave — no importa en
  qué orden esté definida.
- **Ejercicio 6**: diccionario `producto` con valores de distintos tipos
  (`str`, `float`, `int`, `bool`), mostrando que, igual que las listas, un
  diccionario no obliga a que todos los valores sean del mismo tipo.

### Bloque 3 — Estructuras anidadas

- **Ejercicio 7**: `clientes`, una **lista de diccionarios** — el patrón más
  común para representar una tabla o colección de registros en Python puro
  (cada diccionario es una "fila").
- **Ejercicio 8**: `cliente`, un **diccionario que contiene una lista**
  (`compras`), mostrando que los valores de un diccionario pueden ser a su
  vez estructuras compuestas, no solo tipos simples.
- **Ejercicio 9**: `pelicula`, una estructura más realista que combina
  ambos casos (claves con valores simples y una clave `generos` con una
  lista adentro). Punto clave: `pelicula["generos"]` es de tipo `list`,
  mientras que `pelicula["generos"][0]` ya es un `str` — acceder con el
  índice "baja un nivel" en la estructura.

## Capturas de pantalla

Las capturas de pantalla de la ejecución del script (salida por consola de
cada ejercicio) se adjuntan como Anexo en el documento de entrega.

## Uso de IA como apoyo

Al igual que en el resto del repositorio, se utilizó asistencia de IA
(Claude, Anthropic) para mejorar la redacción de este resumen y para apoyo
en la sintaxis del script. La resolución de cada ejercicio y las respuestas
a las preguntas conceptuales son propias.
