
"""
ASGI config for mybotproject project.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mybotproject.settings')

application = get_asgi_application()
