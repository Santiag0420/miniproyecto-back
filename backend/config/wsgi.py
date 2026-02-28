"""
WSGI config for backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path
from django.core.wsgi import get_wsgi_application

# Agrega la raíz del repositorio al path para que 'backend' sea importable
# cuando gunicorn lo ejecuta desde cualquier directorio.
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.config.settings')

application = get_wsgi_application()
