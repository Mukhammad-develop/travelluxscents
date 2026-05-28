"""
Passenger WSGI entry point for cPanel hosting.
This file is used by Phusion Passenger on UnlimitedWebHosting.co.uk cPanel.
"""
import os
import sys

# Add project directory to path
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Add virtualenv site-packages
venv_path = os.path.join(project_home, 'venv', 'lib', 'python3.12', 'site-packages')
if os.path.exists(venv_path):
    sys.path.insert(0, venv_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
