"""
Passenger WSGI entry point for cPanel hosting.
This file is used by Phusion Passenger on UnlimitedWebHosting.co.uk cPanel.
"""
import os
import sys
import glob

# Add project directory to path
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Add virtualenv site-packages - auto-detect Python version
venv_lib = os.path.join(project_home, 'venv', 'lib')
if os.path.exists(venv_lib):
    for site_packages in glob.glob(os.path.join(venv_lib, 'python*', 'site-packages')):
        if site_packages not in sys.path:
            sys.path.insert(0, site_packages)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
