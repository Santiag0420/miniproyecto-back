# miniproyecto-back — Backend

Backend del Proyecto Integrador I, construido con **Django** y **Django REST Framework**, conectado a una base de datos **PostgreSQL** en **Supabase**. Incluye autenticación mediante **JWT**, gestión de actividades evaluativas con subtareas y actualizaciones en tiempo real vía **WebSockets**.

## Descripción

API REST + WebSocket que gestiona usuarios, autenticación y actividades evaluativas. Provee los endpoints que consume el frontend React, incluyendo una vista en tiempo real de las actividades del día.

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
| GET | `/api/activities/today/` | Vista del día: actividades vencidas, de hoy y próximas | Sí |

### Subtareas

| Método | Ruta | Descripción | Auth requerida |
|--------|------|-------------|----------------|
| GET | `/api/activities/<id>/subtasks/` | Lista las subtareas de una actividad | Sí |
| POST | `/api/activities/<id>/subtasks/` | Agrega una subtarea a la actividad | Sí |
| GET | `/api/activities/<id>/subtasks/<id>/` | Detalle de una subtarea | Sí |
| PATCH | `/api/activities/<id>/subtasks/<id>/` | Edita una subtarea | Sí |
| DELETE | `/api/activities/<id>/subtasks/<id>/` | Elimina una subtarea | Sí |

### WebSocket — Vista en tiempo real

| Protocolo | Ruta | Descripción | Auth requerida |
|-----------|------|-------------|----------------|
| WS | `ws/activities/today/?token=<JWT>` | Conexión en tiempo real de la vista del día | Sí (JWT en query string) |

El servidor envía los datos actualizados automáticamente cada vez que el usuario crea, edita o elimina una actividad o subtarea. El cliente también puede enviar cualquier mensaje para forzar un refresco manual.

**Respuesta WebSocket (JSON):**
```json
{
  "vencidas": [ /* actividades con fecha pasada */ ],
  "hoy":      [ /* actividades para hoy */ ],
  "proximas": [ /* actividades futuras o sin fecha */ ]
}
```

Cada actividad en la respuesta incluye todos sus campos más:
- `horas_pendientes`: suma de horas de subtareas no completadas
- `fecha_referencia`: fecha usada para clasificar (`fecha_limite` o `fecha_evento`)

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
  "access": "<token válido 15 minutos>",
  "refresh": "<token válido 30 minutos, se rota en cada uso>"
}
```

> El access token dura 15 minutos. El frontend debe renovarlo antes de que expire usando el refresh token. El refresh token dura 30 minutos desde su último uso — si el usuario no usa la app durante 30 minutos, expira y debe iniciar sesión nuevamente.

#### Crear actividad

```json
POST /api/activities/
Authorization: Bearer <access_token>

{
  "titulo": "Parcial de Bases de Datos",
  "tipo": "exam",
  "curso": "bases_de_datos",
  "fecha_evento": "2025-05-15T10:00:00Z",
  "fecha_limite": "2025-05-15T23:59:00Z"
}
```

> `curso` debe ser uno de los valores definidos en `TipoCurso` (ver tabla de modelos). Las fechas no pueden ser anteriores a la fecha actual.

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

> `fecha_objetivo` debe estar dentro del rango entre `fecha_evento` y `fecha_limite` de la actividad padre.

#### Conectar al WebSocket de la vista del día

```javascript
const token = "<access_token>";
const ws = new WebSocket(`ws://localhost:8000/ws/activities/today/?token=${token}`);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.vencidas, data.hoy, data.proximas);
};

// Forzar refresco manual:
ws.send("refresh");
```

## Tecnologías

- [Python 3.10+](https://www.python.org/) — Lenguaje de programación
- [Django 6.0](https://www.djangoproject.com/) — Framework web
- [Django REST Framework](https://www.django-rest-framework.org/) — Toolkit para APIs REST
- [Django Channels 4](https://channels.readthedocs.io/) — Soporte para WebSockets y comunicación asíncrona
- [djangorestframework-simplejwt](https://django-rest-framework-simplejwt.readthedocs.io/) — Autenticación JWT con rotación de tokens
- [drf-spectacular](https://drf-spectacular.readthedocs.io/) — Documentación automática OpenAPI (Swagger + ReDoc)
- [Daphne](https://github.com/django/daphne) — Servidor ASGI para producción (HTTP + WebSockets)
- [PostgreSQL](https://www.postgresql.org/) — Base de datos relacional
- [Supabase](https://supabase.com/) — Hosting de base de datos en la nube
- [python-dotenv](https://pypi.org/project/python-dotenv/) — Carga de variables de entorno
- [django-cors-headers](https://pypi.org/project/django-cors-headers/) — Manejo de CORS

## Estructura del Proyecto

```
miniproyecto-back/
├── backend/
│   ├── config/                # Configuración central del proyecto Django
│   │   ├── settings.py        # Configuración principal (BD, apps, JWT, CORS, Channels)
│   │   ├── urls.py            # Rutas principales de toda la API
│   │   ├── wsgi.py            # Entrada para servidores WSGI
│   │   └── asgi.py            # Entrada ASGI — maneja HTTP y WebSockets
│   ├── apps/                  # Carpeta que agrupa todas las apps del proyecto
│   │   ├── users/             # App de usuarios y autenticación
│   │   │   ├── models.py      # Modelo Usuario (tabla existente en Supabase)
│   │   │   ├── views.py       # Vistas: listar usuarios y registrar cuenta
│   │   │   ├── urls.py        # Rutas: /api/users/ y /api/users/register/
│   │   │   ├── apps.py        # Configuración de la app
│   │   │   └── admin.py       # Registro en el panel admin
│   │   └── activities/        # App de actividades evaluativas y subtareas
│   │       ├── models.py      # Modelos Activity (con TipoCurso) y SubActivity
│   │       ├── serializers.py # Serializers con validaciones de fechas y rangos
│   │       ├── views.py       # Vistas CRUD + TodayView con notificación WebSocket
│   │       ├── consumers.py   # Consumer WebSocket para la vista en tiempo real
│   │       ├── routing.py     # Rutas WebSocket: ws/activities/today/
│   │       ├── urls.py        # Rutas HTTP: /api/activities/ y subtasks/
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
| `tipo` | CharField | `exam` / `quiz` / `workshop` / `project` / `other` |
| `curso` | CharField(choices) | Curso universitario — ver `TipoCurso` abajo |
| `descripcion` | TextField | Descripción adicional — opcional |
| `fecha_evento` | DateTimeField | Fecha y hora del evento — opcional, no puede ser pasada |
| `fecha_limite` | DateTimeField | Fecha y hora límite de entrega — opcional, no puede ser pasada |
| `fecha_creacion` | DateTimeField | Generada automáticamente al crear |

#### Valores válidos para `curso` (TipoCurso)

| Valor | Descripción |
|-------|-------------|
| `calculo` | Cálculo |
| `algebra` | Álgebra Lineal |
| `estadistica` | Estadística |
| `programacion` | Programación |
| `estructuras_de_datos` | Estructuras de Datos |
| `bases_de_datos` | Bases de Datos |
| `redes` | Redes de Computadores |
| `sistemas_operativos` | Sistemas Operativos |
| `ingenieria_de_software` | Ingeniería de Software |
| `arquitectura` | Arquitectura de Computadores |
| `inteligencia_artificial` | Inteligencia Artificial |
| `fisica` | Física |
| `quimica` | Química |
| `economia` | Economía |
| `contabilidad` | Contabilidad |
| `administracion` | Administración |
| `comunicacion` | Comunicación |
| `humanidades` | Humanidades / Electiva |
| `proyecto_integrador` | Proyecto Integrador |
| `otro` | Otro |

### SubActivity

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | BigAutoField | Identificador único (PK) |
| `activity` | ForeignKey(Activity) | Actividad a la que pertenece |
| `nombre` | CharField(255) | Nombre de la subtarea — obligatorio |
| `fecha_objetivo` | DateField | Fecha objetivo — debe estar dentro del rango de la actividad padre |
| `horas_estimadas` | DecimalField(5,1) | Tiempo estimado en horas (ej: 1.5) — debe ser > 0 |
| `completada` | BooleanField | Indica si la subtarea fue completada |

## Validaciones de negocio

- Las actividades no pueden crearse con `fecha_evento` o `fecha_limite` anteriores a la fecha actual.
- La `fecha_objetivo` de una subtarea debe estar dentro del rango `[fecha_evento, fecha_limite]` de su actividad padre (cuando ambas fechas estén definidas).
- El campo `curso` solo acepta los valores definidos en `TipoCurso`.

## Sesión y tokens JWT

| Token | Duración | Comportamiento |
|-------|----------|----------------|
| Access token | 15 minutos | Se usa en cada request a la API en el header `Authorization: Bearer <token>` |
| Refresh token | 30 minutos | Se rota en cada uso. Si el usuario no usa la app por 30 min, expira y debe volver a iniciar sesión |

El frontend debe renovar el access token antes de que expire (cada ~14 min) usando `POST /api/auth/token/refresh/`. Mientras el usuario esté activo, la sesión se mantiene indefinidamente.

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

# 7. Iniciar el servidor con Daphne (soporta HTTP + WebSockets)
set PYTHONPATH=<ruta-a-miniproyecto-back>
daphne -b 127.0.0.1 -p 8000 backend.config.asgi:application
```

> `python manage.py runserver` **no soporta WebSockets** con Django 6 + Channels 4. Usar Daphne también en desarrollo.

**Ejemplo en Windows (desde la carpeta `backend/`):**
```cmd
set PYTHONPATH=c:\ruta\miniproyecto-back && ..\venv\Scripts\daphne.exe -b 127.0.0.1 -p 8000 backend.config.asgi:application
```

El backend estará disponible en **http://127.0.0.1:8000**

> **Nota Windows:** Si `pip` no funciona directamente, usar `python -m pip install ...`

### Producción (Render)

En producción se usa el mismo comando de Daphne con host y puerto de Render:

```bash
daphne -b 0.0.0.0 -p $PORT backend.config.asgi:application
```

> Daphne ya está incluido en `requirements.txt`. Configura `PYTHONPATH` en las variables de entorno de Render apuntando al directorio raíz del proyecto.

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
| `DEBUG` | Modo debug | `False` en producción |

### Generar una nueva SECRET_KEY

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Seguridad

- Las credenciales sensibles están en `.env` (excluido de git)
- La conexión a Supabase usa SSL con certificado (`prod-ca-2021.crt`)
- Las contraseñas se guardan hasheadas — nunca en texto plano
- Los tokens JWT rotan automáticamente y expiran por inactividad (30 min)
- En producción: cambiar `CORS_ALLOW_ALL_ORIGINS = True` por `CORS_ALLOWED_ORIGINS` con los dominios permitidos
