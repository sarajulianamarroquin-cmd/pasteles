# SweetDreams

Proyecto web con Flask y SQLAlchemy para vender postres premium. Usa SQLite localmente y puede conectarse a MySQL en producción.

## Requisitos

- Python 3.11 o superior
- Visual Studio Code
- Windows PowerShell

## Instalación

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configuración

Copia `.env.example` como `.env` y configura `SECRET_KEY` y `DATABASE_URL`. El `.env` local no se sube a Git. La configuración de desarrollo incluida usa SQLite; para conectar MySQL, establece `DATABASE_URL` con la URL entregada por tu proveedor, por ejemplo:

```text
mysql+pymysql://USUARIO:CONTRASEÑA@HOST:3306/BASE_DE_DATOS?charset=utf8mb4
```

Si tu proveedor entrega una URL que empieza por `mysql://`, la aplicación la adapta automáticamente al driver PyMySQL.

## Base de datos

```powershell
python app.py
```
La aplicación crea las tablas si no existen y añade de forma idempotente el catálogo de 50 productos y 34 recetas detalladas. Las ilustraciones SVG originales se guardan en `static/img/products/`.

Para inicializar el catálogo manualmente:

```powershell
python scripts\initialize_catalog.py
```

## Ejecutar la app

```powershell
python app.py
```
Luego abre http://127.0.0.1:5000

## Despliegue en Render

El archivo `render.yaml` configura el servicio web, la instalación de dependencias y Gunicorn. Render no ofrece MySQL administrado; crea una base MySQL con un proveedor externo y configura `DATABASE_URL` en las variables de entorno del servicio Render con su URL de conexión. Render genera `SECRET_KEY` automáticamente. No subas el `.env` ni pongas credenciales en `render.yaml`.

En Render, usa el directorio raíz del proyecto y despliega el Blueprint definido en `render.yaml`. La base de datos debe aceptar conexiones desde el servicio Render; usa el host, puerto, usuario, contraseña y nombre de base de datos indicados por el proveedor.

## Pruebas

```powershell
pytest -q
```

## Funcionalidades

- Catálogo y búsqueda de productos
- 50 productos con precios en COP e ilustraciones SVG locales
- 34 recetas detalladas, con ingredientes, pasos, tiempo, porciones y dificultad
- Página individual de preparación para cada receta
- Carrito de compras por sesión
- Registro e inicio de sesión
- Checkout con historial de pedidos
- Panel administrativo
