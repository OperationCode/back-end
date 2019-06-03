"""
This file contains all the settings that defines the development server.
SECURITY WARNING: don't run with debug turned on in production!
"""
from settings.components.authentication import MIDDLEWARE
from settings.components.base import INSTALLED_APPS

DEBUG = True

ALLOWED_HOSTS = ["ocbackend.ngrok.io", "localhost", "127.0.0.1"]

if "debug_toolbar" not in INSTALLED_APPS:
    INSTALLED_APPS += ("debug_toolbar",)
if "debug_toolbar.middleware.DebugToolbarMiddleware" not in MIDDLEWARE:
    MIDDLEWARE += ("debug_toolbar.middleware.DebugToolbarMiddleware",)
