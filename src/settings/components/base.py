from settings.components import BASE_DIR, config

SECRET_KEY = config("SECRET_KEY", default="SUPA_SECRET")
TESTING = False

# Application definition
INSTALLED_APPS = [
    # Our apps
    "core.apps.CoreConfig",
    "api.apps.ApiConfig",
    # Default Django apps:
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # Django anymail
    # https://anymail.readthedocs.io/en/stable/
    "anymail",
    # django-background-tasks
    # https://django-background-tasks.readthedocs.io/en/latest/
    "background_task",
    # django-rest-framework
    # https://www.django-rest-framework.org/
    "rest_framework",
    "rest_framework.authtoken",
    "rest_auth.registration",
    # django-rest-auth
    # https://django-rest-auth.readthedocs.io/en/latest/
    "rest_auth",
    # django-allauth
    # https://django-allauth.readthedocs.io/en/latest/installation.html
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.facebook",
    "allauth.socialaccount.providers.github",
    # django-storages
    # https://django-storages.readthedocs.io/en/latest/
    "storages",
    # django-cors-headers
    # https://github.com/ottoyiu/django-cors-headers
    "corsheaders",
    # django-rest-swagger
    # https://django-rest-swagger.readthedocs.io/en/latest/
    "rest_framework_swagger",
]

ROOT_URLCONF = "operationcode_backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR.joinpath("core", "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "operationcode_backend.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": config("DB_ENGINE", default="django.db.backends.sqlite3"),
        "NAME": config("DB_NAME", default=str(BASE_DIR.joinpath("db.sqlite3"))),
        "USER": config("DB_USER", default=""),
        "PASSWORD": config("DB_PASSWORD", default=""),
        "HOST": config("DB_HOST", default=""),
        "PORT": config("DB_PORT", default=""),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True
ATOMIC_REQUESTS = True

EMAIL_BACKEND = config(
    "EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)
DEFAULT_FROM_EMAIL = "noreply@operationcode.org"
SERVER_EMAIL = "noreplyerrors@operationcode.org"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
STATIC_URL = "/static/"
MEDIA_URL = "/media/"
STATIC_ROOT = BASE_DIR.joinpath("static")
MEDIA_ROOT = BASE_DIR.joinpath("media")

SITE_ID = config("SITE_ID", default=3)

ACCOUNT_ADAPTER = "core.adapters.AccountAdapter"
ACCOUNT_USERNAME_REQUIRED = False
