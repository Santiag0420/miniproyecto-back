# 🔙 miniproyecto-back — Backend

Backend del Proyecto Integrador I, construido con **Django** y **Django REST Framework**, conectado a una base de datos **PostgreSQL** en **Supabase**.

## 📋 Descripción

API REST que gestiona los datos de usuarios y actividades. Provee los endpoints que consume el frontend.

### Endpoints disponibles

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Mensaje de bienvenida |
| GET | `/api/users/` | Lista todos los usuarios |
| — | `/admin/` | Panel de administración de Django |

## 🛠️ Tecnologías

- [Python 3](https://www.python.org/) — Lenguaje de programación
- [Django 6.0](https://www.djangoproject.com/) — Framework web
- [Django REST Framework](https://www.django-rest-framework.org/) — Toolkit para APIs REST
- [PostgreSQL](https://www.postgresql.org/) — Base de datos relacional
- [Supabase](https://supabase.com/) — Hosting de base de datos (PostgreSQL en la nube)
- [python-dotenv](https://pypi.org/project/python-dotenv/) — Carga de variables de entorno
- [django-cors-headers](https://pypi.org/project/django-cors-headers/) — Manejo de CORS

## 📁 Estructura del Proyecto

```
miniproyecto-back/
├── backend/
│   ├── backend/               # Configuración del proyecto Django
│   │   ├── __init__.py
│   │   ├── settings.py        # Configuración principal
│   │   ├── urls.py            # Rutas principales
│   │   ├── wsgi.py            # Configuración WSGI
│   │   └── asgi.py            # Configuración ASGI
│   ├── users/                 # App de usuarios
│   │   ├── __init__.py
│   │   ├── admin.py           # Registro en el admin
│   │   ├── apps.py            # Configuración de la app
│   │   ├── models.py          # Modelo Usuario
│   │   ├── urls.py            # Rutas de la app
│   │   ├── views.py           # Vistas / controladores
│   │   └── tests.py           # Tests unitarios
│   └── manage.py              # CLI de Django
├── .env                       # Variables de entorno (no se sube a git)
├── .env.example               # Plantilla de variables de entorno
├── .gitignore                 # Archivos ignorados por git
├── prod-ca-2021.crt           # Certificado SSL para Supabase
├── requirements.txt           # Dependencias de Python
└── README.md                  # Este archivo
```

## 🗃️ Modelo de Datos

### Usuario

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | BigAutoField | Identificador único (PK) |
| `created_at` | DateTimeField | Fecha de creación |
| `name` | CharField(100) | Nombre del usuario |
| `age` | IntegerField | Edad del usuario |

> **Nota:** El modelo usa `managed = False` y `db_table = 'users'`, lo que significa que Django no gestiona la tabla — esta ya existe en Supabase.

## 🚀 Instalación y Ejecución

### Requisitos previos

- [Python 3.10+](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/)

### Pasos

```bash
# 1. Ir a la carpeta del backend
cd miniproyecto-back

# 2. (Opcional) Crear un entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Instalar dependencias
python -m pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con las credenciales de tu base de datos

# 5. Ir a la carpeta donde está manage.py
cd backend

# 6. Iniciar el servidor
python manage.py runserver
```

El backend estará disponible en **http://localhost:8000**

## ⚙️ Variables de Entorno

Crear un archivo `.env` en la raíz de `miniproyecto-back/` con las siguientes variables:

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `DB_NAME` | Nombre de la base de datos | `postgres` |
| `DB_USER` | Usuario de la base de datos | `postgres.xxxxx` |
| `DB_PASSWORD` | Contraseña de la base de datos | `tu_contraseña` |
| `DB_HOST` | Host de la base de datos | `aws-1-us-east-1.pooler.supabase.com` |
| `DB_PORT` | Puerto de la base de datos | `6543` |
| `DJANGO_SECRET_KEY` | Clave secreta de Django | _(generada automáticamente)_ |

### Generar una nueva SECRET_KEY

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 🔒 Seguridad

- Las credenciales sensibles están en `.env` (excluido de git vía `.gitignore`)
- La conexión a Supabase usa SSL con certificado (`prod-ca-2021.crt`)
- CORS está habilitado para permitir conexiones del frontend