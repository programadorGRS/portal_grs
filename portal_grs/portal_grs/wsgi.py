import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal_grs.portal_grs.settings')
application = get_wsgi_application()