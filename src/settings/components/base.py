from settings.components import BASE_DIR, config

SECRET_KEY = config("SECRET_KEY", default="SUPA_SECRET")
TESTING = False

# Application definition
INSTALLED_APPS = [
    # django-jazzmin Admin Console (replaces django-suit)
    # https://django-jazzmin.readthedocs.io/
    "jazzmin",
    # Our apps
    "core.apps.CoreConfig",
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
    # django-q2 (background task queue)
    # https://django-q2.readthedocs.io/
    "django_q",
    # django-rest-framework
    # https://www.django-rest-framework.org/
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    # dj-rest-auth (maintained fork of django-rest-auth)
    # https://dj-rest-auth.readthedocs.io/
    "dj_rest_auth",
    "dj_rest_auth.registration",
    # django-allauth
    # https://django-allauth.readthedocs.io/en/latest/installation.html
    "allauth",
    "allauth.account",
    "allauth.socialaccount",  # Required by dj-rest-auth registration
    # django-storages
    # https://django-storages.readthedocs.io/en/latest/
    "storages",
    # django-cors-headers
    # https://github.com/ottoyiu/django-cors-headers
    "corsheaders",
    # drf-yasg : Yet another Swagger generator
    # https://drf-yasg.readthedocs.io/en/stable/readme.html
    "drf_yasg",
    # django-health-check
    # https://django-health-check.readthedocs.io/en/latest/
    "health_check",  # required
    "health_check.db",  # stock Django health checkers
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

# Django Jazzmin (Admin Console)
# https://django-jazzmin.readthedocs.io/
JAZZMIN_SETTINGS = {
    "site_title": "Operation Code Admin",
    "site_header": "Operation Code",
    "site_brand": "Operation Code",
    "welcome_sign": "Welcome to Operation Code Admin",
    "copyright": "Operation Code",
    "show_sidebar": True,
    "navigation_expanded": True,
    "order_with_respect_to": [
        "auth",
        "core",
        "django_q",
    ],
}

# Django-Q2 configuration (sync mode for testing, use redis/orm in production)
Q_CLUSTER = {
    "name": "operationcode",
    "workers": config("DJANGO_Q_WORKERS", default=1, cast=int),
    "timeout": 60,
    "retry": 120,
    "queue_limit": 50,
    "bulk": 10,
    "orm": "default",  # Use database as broker
}

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
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

SITE_ID = config("SITE_ID", default=3, cast=int)

ACCOUNT_ADAPTER = "core.adapters.AccountAdapter"
# ACCOUNT_USERNAME_REQUIRED moved to authentication.py as ACCOUNT_SIGNUP_FIELDS

# Django 3.2+ default auto field
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
