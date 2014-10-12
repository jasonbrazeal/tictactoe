"""
WSGI config for tictactoe project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
import sys


django_project_dir = os.path.dirname(__file__)
project_dir = os.path.join(os.path.dirname(__file__), '..' )
project_home = os.path.join(os.path.dirname(__file__), '../..' )

if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ['DJANGO_ENVIRONMENT'] = 'dev'
os.environ['DJANGO_SETTINGS_MODULE'] = 'tictactoe.settings.dev'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()