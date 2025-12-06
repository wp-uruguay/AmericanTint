# ERP - American Tint

Sistema de gestión de stock y garantías para polarizados automotrices.

## Características

- Gestión de stock de rollos (Líneas Premium, Nanocarbon, Nanoceramic)
- Sistema de garantías con códigos únicos
- Control de inventario en tiempo real
- Reportes y análisis

## Tecnologías

- Python 3.10+
- Flask 3.0
- SQLAlchemy
- PostgreSQL/SQLite

## Instalación

1. Clonar el repositorio
2. Crear entorno virtual:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Configurar variables de entorno:
   ```bash
   cp .env.example .env
   # Editar .env con tus configuraciones
   ```

5. Inicializar base de datos:
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. Ejecutar aplicación:
   ```bash
   python run.py
   ```

## Estructura del Proyecto

```
ERP/
├── app/              # Aplicación principal
├── migrations/       # Migraciones de BD
├── tests/           # Tests unitarios
└── instance/        # Archivos de instancia
```

## Licencia

Privado - American Tint © 2025
