import datetime
import os

import sentry_sdk
from dotenv import load_dotenv
from sentry_sdk.integrations.django import DjangoIntegration

load_dotenv()

SENTRY_DSN = os.environ.get("SENTRY_DSN")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "local")
RELEASE = os.environ.get("RELEASE", "0.0.0")

if SENTRY_DSN:  # pragma: no cover
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        environment=ENVIRONMENT,
        release=RELEASE,
    )

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DEBUG = os.environ.get("DEBUG") in ("True", "true", "TRUE")
TESTING = False

ALLOWED_HOSTS = ["ocbackend.ngrok.io", "operationcode.org", "pybot.operationcode.org"]

EXTRA_HOSTS = os.environ.get("EXTRA_HOSTS", "")
ALLOWED_HOSTS += [s.strip() for s in EXTRA_HOSTS.split(",") if EXTRA_HOSTS]

if DEBUG:
    ALLOWED_HOSTS += ["localhost", "127.0.0.1"]

# Necessary to allow AWS health check to succeed
try:
    import socket

    local_ip = str(socket.gethostbyname(socket.gethostname()))
    ALLOWED_HOSTS.append(local_ip)
except Exception as ex:  # pragma: no cover
    print(ex)

SECRET_KEY = os.environ.get("SECRET_KEY", "SUPA_SECRET")

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
    "core.apps.CoreConfig",
    "api.apps.ApiConfig",
    "background_task",
    "rest_framework",
    "rest_framework.authtoken",
    "rest_auth",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.facebook",
    "allauth.socialaccount.providers.github",
    "rest_auth.registration",
    "storages",
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
    # Renderer/parsers translate between camelCase and snake_case at application
    # entry, allowing clients to send/receive data as camelCase while we can still
    # use snake_case within this application
    "DEFAULT_RENDERER_CLASSES": (
        "djangorestframework_camel_case.render.CamelCaseJSONRenderer",
    ),
    "DEFAULT_PARSER_CLASSES": (
        "djangorestframework_camel_case.parser.CamelCaseFormParser",
        "djangorestframework_camel_case.parser.CamelCaseMultiPartParser",
        "djangorestframework_camel_case.parser.CamelCaseJSONParser",
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_jwt.authentication.JSONWebTokenAuthentication",
        # "rest_framework.authentication.SessionAuthentication",
    ),
    "JSON_UNDERSCOREIZE": {"no_underscore_before_number": True},
}

ROOT_URLCONF = "operationcode_backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "core", "templates")],
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


if "aws" in ENVIRONMENT:  # pragma: no cover
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
    AWS_STORAGE_BUCKET_NAME = os.environ["AWS_STORAGE_BUCKET_NAME"]
    AWS_S3_REGION_NAME = os.environ["BUCKET_REGION_NAME"]  # e.g. us-east-2
    AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
    AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
    AWS_DEFAULT_ACL = None
    AWS_LOCATION = "static"
    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/"
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"

    STATICFILES_LOCATION = "static"
    MEDIAFILES_LOCATION = "media"
    STATICFILES_STORAGE = "custom_storages.StaticStorage"
    DEFAULT_FILE_STORAGE = "custom_storages.MediaStorage"

else:
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
SITE_ID = os.environ.get("SITE_ID", 3)
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = "email"
REST_USE_JWT = True

# Disabled until front-end is refactored to allow it
# ACCOUNT_EMAIL_VERIFICATION = "mandatory"

ACCOUNT_ADAPTER = "core.adapters.AccountAdapter"
ACCOUNT_USERNAME_REQUIRED = False

JWT_AUTH = {
    "JWT_PAYLOAD_HANDLER": "core.handlers.custom_jwt_payload_handler",
    "JWT_PAYLOAD_GET_USERNAME_HANDLER": "core.handlers.get_username_from_jwt",
    "JWT_AUTH_HEADER_PREFIX": "Bearer",
    "JWT_EXPIRATION_DELTA": datetime.timedelta(hours=1),
    "JWT_ALLOW_REFRESH": False,
    "JWT_AUTH_COOKIE": None,
}

REST_AUTH_SERIALIZERS = {
    "LOGIN_SERIALIZER": "core.serializers.LoginSerializer",
    "USER_DETAILS_SERIALIZER": "core.serializers.UserDetailsSerializer",
}

REST_AUTH_REGISTER_SERIALIZERS = {
    "REGISTER_SERIALIZER": "core.serializers.RegisterSerializer"
}

SOCIALACCOUNT_PROVIDERS = {
    "google": {"SCOPE": ["profile", "email"], "AUTH_PARAMS": {"access_type": "online"}}
}

GITHUB_AUTH_CALLBACK_URL = os.environ.get(
    "GITHUB_AUTH_CALLBACK_URL", "http://localhost:8000/dev/github/login/callback/"
)
