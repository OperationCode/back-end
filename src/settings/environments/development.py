"""
This file contains all the settings that defines the development server.
SECURITY WARNING: don't run with debug turned on in production!
"""
import os

from settings.components.authentication import MIDDLEWARE
from settings.components.base import INSTALLED_APPS

DEBUG = True

ALLOWED_HOSTS = ["ocbackend.ngrok.io", "localhost", "127.0.0.1"]

EXTRA_HOSTS = os.environ.get("EXTRA_HOSTS", "")
ALLOWED_HOSTS += [s.strip() for s in EXTRA_HOSTS.split(",") if EXTRA_HOSTS]

INSTALLED_APPS += ("debug_toolbar",)

MIDDLEWARE += ("debug_toolbar.middleware.DebugToolbarMiddleware",)
