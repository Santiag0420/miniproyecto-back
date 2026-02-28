# miniproyecto-back — Backend

Backend del Proyecto Integrador I, construido con **Django** y **Django REST Framework**, conectado a una base de datos **PostgreSQL** en **Supabase**. Incluye autenticación mediante **JWT** y gestión de actividades evaluativas con sus subtareas.

## Descripción

API REST que gestiona usuarios, autenticación y actividades evaluativas. Provee los endpoints que consume el frontend React.

## Documentación interactiva de la API

| Interfaz | Ruta | Descripción |
|---|---|---|
| Swagger UI | `/api/docs/` | Interfaz visual para explorar y probar los endpoints |
| ReDoc | `/api/redoc/` | Vista de documentación alternativa más legible |
| Esquema OpenAPI | `/api/schema/` | Esquema en formato JSON/YAML para importar en Postman u otras herramientas |

## Endpoints disponibles

### Autenticación y usuarios

| Método | Ruta | Descripción | Auth requerida |
|--------|------|-------------|----------------|
| GET | `/` | Mensaje de bienvenida | No |
| GET | `/admin/` | Panel de administración de Django | No |
| GET | `/api/users/` | Lista todos los usuarios de Supabase | No |
| POST | `/api/users/register/` | Registrar nuevo usuario | No |
| POST | `/api/auth/login/` | Iniciar sesión — devuelve `access` y `refresh` tokens | No |
| POST | `/api/auth/token/refresh/` | Renovar el access token usando el refresh token | No |

### Actividades

| Método | Ruta | Descripción | Auth requerida |
|--------|------|-------------|----------------|
| GET | `/api/activities/` | Lista las actividades del usuario autenticado | Sí |
| POST | `/api/activities/` | Crea una nueva actividad | Sí |
| GET | `/api/activities/<id>/` | Detalle de una actividad con sus subtareas | Sí |
| PATCH | `/api/activities/<id>/` | Edita una actividad | Sí |
| DELETE | `/api/activities/<id>/` | Elimina una actividad y todas sus subtareas | Sí |

### Subtareas

| Método | Ruta | Descripción | Auth requerida |
|--------|------|-------------|----------------|
| GET | `/api/activities/<id>/subtasks/` | Lista las subtareas de una actividad | Sí |
| POST | `/api/activities/<id>/subtasks/` | Agrega una subtarea a la actividad | Sí |
| GET | `/api/activities/<id>/subtasks/<id>/` | Detalle de una subtarea | Sí |
| PATCH | `/api/activities/<id>/subtasks/<id>/` | Edita una subtarea | Sí |
| DELETE | `/api/activities/<id>/subtasks/<id>/` | Elimina una subtarea | Sí |

## Ejemplos de uso

#### Registrar usuario

```json
POST /api/users/register/
{
  "username": "juanito",
  "email": "juan@email.com",
  "password": "mipassword123"
}
```

#### Login

```json
POST /api/auth/login/
{
  "username": "juanito",
  "password": "mipassword123"
}
```

Respuesta:
```json
{
  "access": "<token de corta duración>",
  "refresh": "<token de larga duración>"
}
```

#### Crear actividad

```json
POST /api/activities/
Authorization: Bearer <access_token>

{
  "titulo": "Parcial de Bases de Datos",
  "tipo": "exam",
  "curso": "Bases de Datos I",
  "fecha_evento": "2025-05-15T10:00:00Z",
  "fecha_limite": "2025-05-15"
}
```

#### Agregar subtarea

```json
POST /api/activities/1/subtasks/
Authorization: Bearer <access_token>

{
  "nombre": "Repasar normalización",
  "fecha_objetivo": "2025-05-12",
  "horas_estimadas": 2.5
}
```

## Tecnologías

- [Python 3.14](https://www.python.org/) — Lenguaje de programación
- [Django 6.0](https://www.djangoproject.com/) — Framework web
- [Django REST Framework](https://www.django-rest-framework.org/) — Toolkit para APIs REST
- [djangorestframework-simplejwt](https://django-rest-framework-simplejwt.readthedocs.io/) — Autenticación JWT
- [drf-spectacular](https://drf-spectacular.readthedocs.io/) — Documentación automática OpenAPI (Swagger + ReDoc)
- [Gunicorn](https://gunicorn.org/) — Servidor WSGI para producción
- [PostgreSQL](https://www.postgresql.org/) — Base de datos relacional
- [Supabase](https://supabase.com/) — Hosting de base de datos en la nube
- [python-dotenv](https://pypi.org/project/python-dotenv/) — Carga de variables de entorno
- [django-cors-headers](https://pypi.org/project/django-cors-headers/) — Manejo de CORS

## Estructura del Proyecto

```
miniproyecto-back/
├── backend/
│   ├── config/                # Configuración central del proyecto Django
│   │   ├── settings.py        # Configuración principal (BD, apps, JWT, CORS)
│   │   ├── urls.py            # Rutas principales de toda la API
│   │   ├── wsgi.py            # Entrada para servidores WSGI (producción)
│   │   └── asgi.py            # Entrada para servidores ASGI (async)
│   ├── apps/                  # Carpeta que agrupa todas las apps del proyecto
│   │   ├── users/             # App de usuarios y autenticación
│   │   │   ├── models.py      # Modelo Usuario (tabla existente en Supabase)
│   │   │   ├── views.py       # Vistas: listar usuarios y registrar cuenta
│   │   │   ├── urls.py        # Rutas: /api/users/ y /api/users/register/
│   │   │   ├── apps.py        # Configuración de la app
│   │   │   └── admin.py       # Registro en el panel admin
│   │   └── activities/        # App de actividades evaluativas y subtareas
│   │       ├── models.py      # Modelos Activity y SubActivity
│   │       ├── serializers.py # Serializers con validaciones de campos
│   │       ├── views.py       # Vistas CRUD con aislamiento por usuario
│   │       ├── urls.py        # Rutas: /api/activities/ y subtasks/
│   │       ├── apps.py        # Configuración de la app
│   │       └── admin.py       # Registro en el panel admin
│   └── manage.py              # CLI de Django
├── .env                       # Variables de entorno (NO subir a git)
├── prod-ca-2021.crt           # Certificado SSL para conexión segura a Supabase
├── requirements.txt           # Dependencias exactas de Python
└── README.md                  # Este archivo
```

## Modelos de Datos

### Usuario (tabla `users` — existente en Supabase)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | BigAutoField | Identificador único (PK) |
| `created_at` | DateTimeField | Fecha de creación |
| `name` | CharField(100) | Nombre del usuario |
| `age` | IntegerField | Edad del usuario |

> `managed = False` indica que Django no crea ni modifica esta tabla con migraciones — ya existe en Supabase.

### User de Django (`auth_user` — gestionada por Django)

Tabla estándar de Django usada para el sistema de autenticación (login/register con JWT). Se crea ejecutando `python manage.py migrate`.

### Activity

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | BigAutoField | Identificador único (PK) |
| `usuario` | ForeignKey(User) | Usuario dueño de la actividad |
| `titulo` | CharField(255) | Nombre de la actividad — obligatorio |
| `tipo` | CharField | exam / quiz / workshop / project / other |
| `curso` | CharField(255) | Nombre del curso — obligatorio |
| `descripcion` | TextField | Descripción adicional — opcional |
| `fecha_evento` | DateTimeField | Fecha y hora del evento — opcional |
| `fecha_limite` | DateField | Fecha límite de entrega — opcional |
| `fecha_creacion` | DateTimeField | Generada automáticamente al crear |

### SubActivity

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | BigAutoField | Identificador único (PK) |
| `activity` | ForeignKey(Activity) | Actividad a la que pertenece |
| `nombre` | CharField(255) | Nombre de la subtarea — obligatorio |
| `fecha_objetivo` | DateField | Fecha objetivo para completarla — obligatorio |
| `horas_estimadas` | DecimalField(5,1) | Tiempo estimado en horas (ej: 1.5) — debe ser > 0 |
| `completada` | BooleanField | Indica si la subtarea fue completada |

## Instalación y Ejecución

### Requisitos previos

- [Python 3.10+](https://www.python.org/downloads/)

### Pasos

```bash
# 1. Ir a la carpeta del backend
cd miniproyecto-back/backend

# 2. Crear un entorno virtual
python -m venv venv

# 3. Activar el entorno virtual
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 4. Instalar dependencias
python -m pip install -r ../requirements.txt

# 5. Configurar variables de entorno
# Crear el archivo .env en miniproyecto-back/ con las variables listadas abajo

# 6. Crear las tablas en la base de datos
python manage.py migrate

# 7. Iniciar el servidor
python manage.py runserver
```

El backend estará disponible en **http://localhost:8000**

> **Nota Windows:** Si `pip` no funciona directamente, usar `python -m pip install ...`

## Variables de Entorno

Crear un archivo `.env` en `miniproyecto-back/` con las siguientes variables:

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `DB_NAME` | Nombre de la base de datos | `postgres` |
| `DB_USER` | Usuario de la base de datos | `postgres.xxxxx` |
| `DB_PASSWORD` | Contraseña de la base de datos | `tu_contraseña` |
| `DB_HOST` | Host de Supabase | `aws-1-us-east-1.pooler.supabase.com` |
| `DB_PORT` | Puerto de la base de datos | `6543` |
| `DJANGO_SECRET_KEY` | Clave secreta de Django | _(ver comando abajo)_ |

### Generar una nueva SECRET_KEY

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Seguridad

- Las credenciales sensibles están en `.env` (excluido de git)
- La conexión a Supabase usa SSL con certificado (`prod-ca-2021.crt`)
- Las contraseñas se guardan hasheadas — nunca en texto plano
- Los tokens JWT tienen tiempo de expiración configurable en `settings.py`
- En producción: cambiar `CORS_ALLOW_ALL_ORIGINS = True` por `CORS_ALLOWED_ORIGINS` con los dominios permitidos
