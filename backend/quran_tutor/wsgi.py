"""
WSGI config for quran_tutor project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quran_tutor.settings')
application = get_wsgi_application()
