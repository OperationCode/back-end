"""
This file contains all the settings that defines the development server.
SECURITY WARNING: don't run with debug turned on in production!
"""
from settings.components.authentication import MIDDLEWARE
from settings.components.base import INSTALLED_APPS

DEBUG = True

ALLOWED_HOSTS = ["ocbackend.ngrok.io", "localhost", "127.0.0.1"]

INSTALLED_APPS += ("debug_toolbar",)

MIDDLEWARE += ("debug_toolbar.middleware.DebugToolbarMiddleware",)
