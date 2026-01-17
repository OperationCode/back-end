from datetime import timedelta

from settings.components import config

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
)

MIDDLEWARE = [
    # Corsheaders:
    "corsheaders.middleware.CorsMiddleware",
    # Django:
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # Required by django-allauth
    "allauth.account.middleware.AccountMiddleware",
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

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# dj-rest-auth settings
# https://dj-rest-auth.readthedocs.io/
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = "email"
REST_USE_JWT = True

REST_AUTH = {
    "LOGIN_SERIALIZER": "core.serializers.LoginSerializer",
    "USER_DETAILS_SERIALIZER": "core.serializers.UserDetailsSerializer",
    "PASSWORD_RESET_CONFIRM_SERIALIZER": "core.serializers.PasswordResetConfirmSerializer",
    "REGISTER_SERIALIZER": "core.serializers.RegisterSerializer",
    "USE_JWT": True,
    "JWT_AUTH_HTTPONLY": False,
    # Custom JWT serializer that adds 'token' for backwards compatibility with PyBot
    "JWT_SERIALIZER": "core.handlers.BackwardsCompatibleJWTSerializer",
}

# Load JWT keys
jwt_secret_key = config("JWT_SECRET_KEY", default=open(".dev/dev-jwt-key").read())
jwt_public_key = config("JWT_PUBLIC_KEY", default=open(".dev/dev-jwt-key.pub").read())

# Simple JWT settings (replaces djangorestframework-jwt)
# https://django-rest-framework-simplejwt.readthedocs.io/
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "ALGORITHM": "RS256",
    "SIGNING_KEY": jwt_secret_key,
    "VERIFYING_KEY": jwt_public_key,
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "TOKEN_OBTAIN_SERIALIZER": "core.handlers.CustomTokenObtainPairSerializer",
}

CORS_ORIGIN_ALLOW_ALL = True
