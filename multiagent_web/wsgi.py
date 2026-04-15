"""WSGI config for multiagent_web project."""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "multiagent_web.settings")

application = get_wsgi_application()
