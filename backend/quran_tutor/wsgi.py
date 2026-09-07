"""
WSGI config for quran_tutor project.
"""
import os
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
root_dir = backend_dir.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quran_tutor.settings')
application = get_wsgi_application()
