"""
Soluciones: Listas y Diccionarios en Python
Bloque 1: Listas (ejercicios 1-3)
Bloque 2: Diccionarios (ejercicios 4-6)
Bloque 3: Estructuras anidadas (ejercicios 7-9)
"""

# ============================================================
# BLOQUE 1 - LISTAS
# ============================================================

# --- Ejercicio 1: Crear una lista ---
edades = [18, 21, 25, 30, 35]

print(edades)
print(type(edades))
print(type(edades[0]))
print(type(edades[-1]))
print(edades[2])


# --- Ejercicio 2: Lista heterogenea ---
datos = ["Ana", 25, 1.72, True]

print(f"El objeto datos es de tipo: {type(datos)}")
print(type(datos[0]))
print(type(datos[1]))
print(type(datos[2]))
print(type(datos[3]))


# --- Ejercicio 3: Acceso por indice ---
ciudades = [
    "Montevideo",
    "Salto",
    "Paysandu",
    "Maldonado",
    "Colonia"
]

print(ciudades[0])   # "Montevideo"
print(ciudades[2])   # "Paysandu"
print(ciudades[4])   # "Colonia"
print(ciudades[-1])  # ultimo elemento con indice negativo

# Extra: ciudades[5] lanza IndexError: list index out of range
# porque la lista solo tiene indices del 0 al 4


# ============================================================
# BLOQUE 2 - DICCIONARIOS
# ============================================================

# --- Ejercicio 4: Crear un diccionario ---
persona = {
    "nombre": "Martina",
    "edad": 22,
    "altura": 1.68,
    "estudiante": True
}

print(persona)
print(type(persona))
print(type(persona["nombre"]))
print(type(persona["edad"]))
print(type(persona["altura"]))
print(type(persona["estudiante"]))


# --- Ejercicio 5: Acceso por clave ---
print(f"Nombre: {persona['nombre']}")
print(f"Edad: {persona['edad']}")
print(f"Altura: {persona['altura']}")
print(f"Es estudiante: {persona['estudiante']}")


# --- Ejercicio 6: Diccionario heterogeneo ---
producto = {
    "nombre": "Notebook",
    "precio": 1250.50,
    "stock": 15,
    "disponible": True
}

for clave, valor in producto.items():
    print(f"{valor}\t-> {type(valor).__name__}")


# ============================================================
# BLOQUE 3 - ESTRUCTURAS ANIDADAS
# ============================================================

# --- Ejercicio 7: Lista de diccionarios ---
clientes = [
    {"nombre": "Ana", "edad": 25},
    {"nombre": "Juan", "edad": 31},
    {"nombre": "Pedro", "edad": 28}
]

print(type(clientes))
print(type(clientes[0]))
print(clientes[0]["nombre"])  # Ana
print(clientes[1]["edad"])    # 31
print(clientes[2]["nombre"])  # Pedro


# --- Ejercicio 8: Diccionario que contiene una lista ---
cliente = {
    "nombre": "Ana",
    "edad": 25,
    "compras": [120, 350, 80]
}

print(cliente["nombre"], cliente["edad"])
print(cliente["compras"])
print(cliente["compras"][0])
print(cliente["compras"][-1])


# --- Ejercicio 9: Estructura mas realista ---
pelicula = {
    "titulo": "Matrix",
    "anio": 1999,
    "duracion": 136,
    "generos": ["Ciencia ficcion", "Accion"],
    "activa": True
}

print(pelicula["titulo"], type(pelicula["titulo"]))
print(pelicula["anio"], type(pelicula["anio"]))
print(pelicula["duracion"], type(pelicula["duracion"]))
print(pelicula["generos"][0], type(pelicula["generos"][0]))
print(pelicula["generos"][1], type(pelicula["generos"][1]))
print(pelicula["activa"], type(pelicula["activa"]))

# Comparacion: type(pelicula["generos"]) es list (la lista completa)
# type(pelicula["generos"][0]) es str (un elemento de esa lista)
# Son distintos porque "generos" es una estructura (list) que contiene
# elementos individuales (str) — el anidamiento es justamente eso.
