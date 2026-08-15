En la terminal, dentro del repo:

```bash
source .venv/bin/activate
python practica_listas_diccionarios.py
```

Si el venv todavía no existe:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

En VS Code, además, conviene fijar el intérprete para que el editor use ese mismo entorno (autocompletado, linter, etc.):

1. `Cmd+Shift+P` → **Python: Select Interpreter**
2. Elegí el que apunta a `./.venv/bin/python`

Con eso seleccionado, el botón de **Run** (▶) de la esquina superior derecha o `Cmd+Shift+D` (Run and Debug) ya corre el script con ese venv, sin necesidad de activarlo a mano en la terminal integrada.

Para salir del venv cuando termines: `deactivate`.