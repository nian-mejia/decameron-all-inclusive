# Decameron Multivaciones

Aplicación para gestionar reservas de hoteles Decameron.

## Requisitos

- Python 3.9 o superior
- uv (instalador moderno de paquetes Python)

## Instalación

1. Instalar uv si aún no lo tienes:
```bash
pip install uv
```

2. Clonar el repositorio:
```bash
git clone git@github.com:nian-mejia/decameron-all-inclusive.git
cd Multivaciones
```

3. Crear y activar el entorno virtual con uv:
```bash
uv venv
source .venv/bin/activate  # En Unix/MacOS
# O en Windows:
# .venv\Scripts\activate
```

4. Instalar dependencias con uv y pyproject.toml:
```bash
uv pip install -r pyproject.toml
```

## Ejecutar la aplicación

```bash
python3 src/main.py
```

## Desarrollo

Para agregar nuevas dependencias, edita el bloque `[project].dependencies` en `pyproject.toml` y luego ejecuta:
```bash
uv add ruff
```

Para actualizar dependencias a las últimas versiones compatibles:
```bash
uv pip install --upgrade pyproject.toml
``` 