"""ASGI config for cadastro_pessoas project."""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cadastro_pessoas.settings')
application = get_asgi_application()
