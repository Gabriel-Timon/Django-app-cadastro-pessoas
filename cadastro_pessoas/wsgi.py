"""WSGI config for cadastro_pessoas project."""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cadastro_pessoas.settings')
application = get_wsgi_application()
