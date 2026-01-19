"""
This file contains all the settings that defines the development server.
SECURITY WARNING: don't run with debug turned on in production!
"""
from settings.components.authentication import MIDDLEWARE
from settings.components.base import INSTALLED_APPS

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "*.ngrok.io", "*.ngrok-free.app"]

# Required for Django 4.0+ CSRF protection with HTTPS (ngrok uses HTTPS)
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://*.ngrok.io",
    "https://*.ngrok-free.app",
]

if "debug_toolbar" not in INSTALLED_APPS:
    INSTALLED_APPS += ("debug_toolbar",)
if "debug_toolbar.middleware.DebugToolbarMiddleware" not in MIDDLEWARE:
    MIDDLEWARE += ("debug_toolbar.middleware.DebugToolbarMiddleware",)
