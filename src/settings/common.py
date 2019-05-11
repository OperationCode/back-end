import datetime
import os

from dotenv import load_dotenv  # noqa

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# APPEND_SLASH = False

# TODO: CHANGE THIS BEFORE PROD PLEASE!
ALLOWED_HOSTS = ["*"]

ADMINS = (("Admin", "example@example.com"),)

SECRET_KEY = os.environ.get(
    "SECRET_KEY", "&e4+qaiwz$+ie#kx9=f%w1)pzmr#b$&^)6jl&c)ad_i*670trt"
)

DEBUG = False

CORS_ORIGIN_ALLOW_ALL = True

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "backend.apps.BackendConfig",
    "api.apps.ApiConfig",
    "background_task",
    "rest_framework",
    "rest_framework.authtoken",
    "rest_auth",
    "allauth",
    "allauth.account",
    "rest_auth.registration",
    "corsheaders",
    "rest_framework_swagger",
]

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
)

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.BCryptPasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.Argon2PasswordHasher",
]

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_jwt.authentication.JSONWebTokenAuthentication",
        # 'rest_framework.authentication.TokenAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
    ),
}

ROOT_URLCONF = "operationcode_backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
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
        "ENGINE": os.environ.get("ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("NAME", os.path.join(BASE_DIR, "db.sqlite3")),
        "USER": os.environ.get("USER", ""),
        "PASSWORD": os.environ.get("PASSWORD", ""),
        "HOST": os.environ.get("HOST", ""),
        "PORT": os.environ.get("PORT", ""),
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

ATOMIC_REQUESTS = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = "/static/"
MEDIA_URL = "/media/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

PYBOT_AUTH_TOKEN = os.environ.get("PYBOT_AUTH_TOKEN", "")
PYBOT_URL = os.environ.get("PYBOT_URL", "http://localhost:5000")

MAILCHIMP_API_KEY = os.environ.get("MAILCHIMP_API_KEY", "")
MAILCHIMP_USERNAME = os.environ.get("MAILCHIMP_USERNAME", "")
MAILCHIMP_LIST_ID = os.environ.get("MAILCHIMP_LIST_ID", "")

EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_PORT = os.environ.get("EMAIL_PORT", "")

# Django-Rest-Auth
REST_SESSION_LOGIN = True
SITE_ID = 3
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
REST_USE_JWT = True
# ACCOUNT_EMAIL_CONFIRMATION_HMAC = False

ACCOUNT_ADAPTER = "backend.adapters.AccountAdapter"
ACCOUNT_USERNAME_REQUIRED = False

JWT_AUTH = {
    "JWT_PAYLOAD_HANDLER": "backend.handlers.custom_jwt_payload_handler",
    "JWT_PAYLOAD_GET_USERNAME_HANDLER": "backend.handlers.get_username_from_jwt",
    "JWT_AUTH_HEADER_PREFIX": "Bearer",
    "JWT_EXPIRATION_DELTA": datetime.timedelta(seconds=300),
    "JWT_ALLOW_REFRESH": True,
    "JWT_AUTH_COOKIE": "JWT",
}

REST_AUTH_SERIALIZERS = {
    "LOGIN_SERIALIZER": "backend.serializers.CustomLoginSerializer"
}
