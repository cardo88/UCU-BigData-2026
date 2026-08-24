"""
Practica: Listas y Diccionarios en Python
Bloque 1: Listas (ejercicios 1-3)
Bloque 2: Diccionarios (ejercicios 4-6)
Bloque 3: Estructuras anidadas (ejercicios 7-9)
"""

# ============================================================
# BLOQUE 1 - LISTAS
# ============================================================

# --- Ejercicio 1: Crear una lista ---
print("\n--- Ejercicio 1: Crear una lista ---")
edades = [18, 21, 25, 30, 35]

# Actividades:
# 1. Mostrar la lista completa
print(edades)
# 2. Mostrar type(edades)
print(type(edades))
# 3. Mostrar el tipo del primer elemento
print(type(edades[0]))
# 4. Mostrar el tipo del ultimo elemento
print(type(edades[-1]))
# 5. Acceder al tercer elemento por indice
print(edades[2])



print("\nPreguntas:")
print("1. ¿Qué tipo infiere Python para edades?", type(edades))
print("2. ¿Qué tipo tienen sus elementos?", type(edades[0]))
print("3. ¿Cuál es el índice del primer elemento?", 0)



# --- Ejercicio 2: Lista heterogenea ---
print("\n--- Ejercicio 2: Lista heterogenea ---")
datos = ["Ana", 25, 1.72, True]

# Actividades:
# 1. Imprimir: "El objeto datos es de tipo: ...
print(f"El objeto datos es de tipo: {type(datos)}")
# 2. Imprimir el tipo del 1ro, 2do, 3ro y 4to elemento usando type()
print(f"El tipo del primer elemento es: {type(datos[0])}")
print(f"El tipo del segundo elemento es: {type(datos[1])}")
print(f"El tipo del tercer elemento es: {type(datos[2])}")
print(f"El tipo del cuarto elemento es: {type(datos[3])}")


print("\nPreguntas:")
print("1. ¿Todos los elementos tienen el mismo tipo?", len(set(type(x) for x in datos)) == 1)
print("2. ¿Python permite mezclar tipos en una lista?", True)
print("3. ¿Qué tipo tiene la lista en sí misma?", type(datos))


# --- Ejercicio 3: Acceso por indice ---
print("\n--- Ejercicio 3: Acceso por indice ---")
ciudades = [
    "Montevideo",
    "Salto",
    "Paysandu",
    "Maldonado",
    "Colonia"
]


# Obtener:
# 1. "Montevideo"
print(ciudades[0])
# 2. "Paysandu"
print(ciudades[2])
# 3. "Colonia"
print(ciudades[4])
# 4. El ultimo elemento usando un indice negativo
print(ciudades[-1])
# Extra: probar ciudades[5] y observar el error
print("Intentando acceder a ciudades[5]:")
try:
    print(ciudades[5])
except IndexError as e:
    print(f"Error: {e}")

print("\nPreguntas:")
print("1. En una lista, los elementos son accedidos mediante: índices.")
print("2. Si intentampos acceder a ciudades[5], Python muestra un error:")
print("IndexError: list index out of range")
print("Esto ocurre porque el índice 5 no existe en la lista, que va desde 0 hasta 4.")


# ============================================================
# BLOQUE 2 - DICCIONARIOS
# ============================================================
print("\n--- Ejercicio 4: Crear un diccionario ---")
print("\nEjercicio 4: Crear un diccionario")
persona = {
    "nombre": "Martina",
    "edad": 22,
    "altura": 1.68,
    "estudiante": True
}


# Actividades:
# 1. Mostrar persona completo
print(persona)
# 2. Mostrar type(persona)
print(type(persona))
# 3. Mostrar el tipo del valor de cada clave: nombre, edad, altura, estudiante
print(type(persona["nombre"]))
print(type(persona["edad"]))
print(type(persona["altura"]))
print(type(persona["estudiante"]))


print("\nPreguntas:")
print("1. En un diccionario, los valores son accedidos mediante: claves.")


# --- Ejercicio 5: Acceso por clave ---
print("\n--- Ejercicio 5: Acceso por clave ---")
# Usando el diccionario "persona" del ejercicio anterior, producir la salida:
# Nombre: Martina
# Edad: 22
# Altura: 1.68
# Es estudiante: True
print(f"Nombre: {persona['nombre']}")
print(f"Edad: {persona['edad']}")
print(f"Altura: {persona['altura']}")
print(f"Es estudiante: {persona['estudiante']}")


print("\nPreguntas:")
print("1. ¿Qué diferencia hay entre  ciudades[2]  y  persona['edad'] ?")
print("'ciudades[2]' accede a un elemento de una lista mediante un índice,")
print("mientras que 'persona[\"edad\"]' accede a un valor de un diccionario mediante una clave.")


# --- Ejercicio 6: Diccionario heterogeneo ---
print("\n--- Ejercicio 6: Diccionario heterogeneo ---")
producto = {
    "nombre": "Notebook",
    "precio": 1250.50,
    "stock": 15,
    "disponible": True
}

# Para cada elemento, mostrar su valor y su tipo, por ejemplo:
# Notebook   -> str
# 1250.50    -> float
# 15         -> int
# True       -> bool
print(f"{producto['nombre']} -> {type(producto['nombre']).__name__}")
print(f"{producto['precio']} -> {type(producto['precio']).__name__}")
print(f"{producto['stock']} -> {type(producto['stock']).__name__}")
print(f"{producto['disponible']} -> {type(producto['disponible']).__name__}")

print("\nPreguntas:")
print("1. ¿Puede un diccionario contener valores de diferentes tipos?")
print("Si, como se observa en el diccionario 'producto', que contiene str, float, int y bool.")


# ============================================================
# BLOQUE 3 - ESTRUCTURAS ANIDADAS
# ============================================================
print("\n--- Ejercicio 7: Lista de diccionarios ---")
clientes = [
    {"nombre": "Ana", "edad": 25},
    {"nombre": "Juan", "edad": 31},
    {"nombre": "Pedro", "edad": 28}
]

# Actividades:
# 1. Mostrar type(clientes) y type(clientes[0])
# 2. Obtener el nombre de Ana
# 3. Obtener la edad de Juan
# 4. Obtener el nombre de Pedro
print(type(clientes))
print(type(clientes[0]))
print(clientes[0]["nombre"])
print(clientes[1]["edad"])
print(clientes[2]["nombre"])


# --- Ejercicio 8: Diccionario que contiene una lista ---
print("\n--- Ejercicio 8: Diccionario que contiene una lista ---")
cliente = {
    "nombre": "Ana",
    "edad": 25,
    "compras": [120, 350, 80]
}

# Obtener:
# 1. El nombre y la edad
# 2. La lista completa de compras
# 3. La primera compra
# 4. La ultima compra (usando indice negativo)
print(cliente["nombre"], cliente["edad"])
print(cliente["compras"])
print(cliente["compras"][0])
print(cliente["compras"][-1])

print("\nPreguntas:")
print("1. ¿Qué tipos de objetos hay dentro de cliente?")
print("El diccionario 'cliente' contiene una cadena de texto (str),")
print("un número entero (int) y una lista (list).")

# --- Ejercicio 9: Estructura mas realista ---
print("\n--- Ejercicio 9: Estructura mas realista ---")
pelicula = {
    "titulo": "Matrix",
    "anio": 1999,
    "duracion": 136,
    "generos": ["Ciencia ficcion", "Accion"],
    "activa": True
}

# Obtener y mostrar el tipo de cada uno:
# 1. Titulo, anio, duracion
# 2. Primer genero y segundo genero
# 3. Estado (activa)
# Pregunta: comparar el tipo de pelicula["generos"] con pelicula["generos"][0]
print(type(pelicula["titulo"]))
print(type(pelicula["anio"]))
print(type(pelicula["duracion"]))
print(pelicula["generos"][0])
print(pelicula["generos"][1])
print(type(pelicula["activa"]))

print("\nPreguntas:")
print("1. Comparar el tipo de pelicula[\"generos\"] con pelicula[\"generos\"][0]")
print("El tipo de pelicula[\"generos\"] es <class 'list'>,")
print("mientras que el tipo de pelicula[\"generos\"][0] es <class 'str'>.")