from settings.components.base import INSTALLED_APPS
from settings.components.rest import REST_FRAMEWORK

# noinspection PyUnresolvedReferences
MEDIA_ROOT = "/tmp"  # nosec
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
TESTING = True

REST_FRAMEWORK = {**REST_FRAMEWORK, "TEST_REQUEST_DEFAULT_FORMAT": "json"}

INSTALLED_APPS += ["tests"]

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": "db.sqlite3"}}

# Temporary frontend configs
RECAPTCHA_DISABLE = True
