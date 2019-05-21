from .development import *  # noqa: F403

MEDIA_ROOT = "/tmp"
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
DEBUG = True
TESTING = True

REST_FRAMEWORK = {**REST_FRAMEWORK, "TEST_REQUEST_DEFAULT_FORMAT": "json"}

INSTALLED_APPS = INSTALLED_APPS + ["tests"]  # noqa: F405

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),  # noqa: F405
    }
}
