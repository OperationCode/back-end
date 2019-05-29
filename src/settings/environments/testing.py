from settings.components.rest import REST_FRAMEWORK

MEDIA_ROOT = "/tmp"  # nosec
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
TESTING = True

REST_FRAMEWORK = {**REST_FRAMEWORK, "TEST_REQUEST_DEFAULT_FORMAT": "json"}

INSTALLED_APPS = INSTALLED_APPS + ["tests"]  # noqa: F405

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(BASE_DIR.joinpath("db.sqlite3")),  # noqa: F405
    }
}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"  # noqa
