"""
ASGI config for backend project.

Maneja conexiones HTTP (Django normal) y WebSocket (Django Channels).
Las rutas WebSocket se definen en backend/apps/activities/routing.py.
"""

import os
import sys
from pathlib import Path

from django.core.asgi import get_asgi_application

root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.config.settings')

# Inicializar Django antes de importar consumers (que usan modelos).
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from backend.apps.activities.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': URLRouter(websocket_urlpatterns),
})
