import warnings
from datetime import timedelta

from settings.components import config

# Suppress dj-rest-auth deprecation warnings (they haven't updated for allauth v65+ yet)
# These are cosmetic - functionality still works
warnings.filterwarnings(
    "ignore",
    message="app_settings.*is deprecated",
    category=UserWarning,
    module="dj_rest_auth.registration.serializers",
)

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
    # Primary hasher for new passwords - Argon2 with tuned params (~200-300ms)
    # Uses memory_cost=19456 (19 MB, vs Django default 100 MB) for better performance
    # while maintaining OWASP-recommended security. Configured in core/hashers.py
    "core.hashers.TunedArgon2PasswordHasher",
    # Legacy hashers - kept to verify existing passwords (auto-upgrade on login)
    "django.contrib.auth.hashers.BCryptPasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
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

# django-allauth settings (v65+)
# https://docs.allauth.org/en/latest/account/configuration.html
ACCOUNT_LOGIN_METHODS = {"email"}  # Replaces ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_SIGNUP_FIELDS = [
    "email*",      # Required (replaces ACCOUNT_EMAIL_REQUIRED = True)
    "password1*",
    "password2*",
    # Note: username not included (replaces ACCOUNT_USERNAME_REQUIRED = False)
]

# dj-rest-auth settings
# https://dj-rest-auth.readthedocs.io/
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

# Load JWT secret key
# For HS256 (HMAC), we only need a shared secret (simple string, not RSA keypair)
# Note: In production, set JWT_SECRET_KEY env var to a strong random secret
# Development default: Use a simple string since HS256 needs symmetric key
jwt_secret_key = config(
    "JWT_SECRET_KEY",
    default="dev-secret-key-change-in-production-to-something-secure-and-random"
)

# Simple JWT settings (replaces djangorestframework-jwt)
# https://django-rest-framework-simplejwt.readthedocs.io/
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "AUTH_HEADER_TYPES": ("Bearer",),
    # HS256 (HMAC-SHA256) is 10-20x faster than RS256 (RSA) for signing/verification
    # Reduces JWT generation from ~270ms to ~15ms per token
    # Trade-off: Requires shared secret (vs public key distribution), but fine for
    # backend-only verification where tokens are opaque to external services
    "ALGORITHM": "HS256",
    "SIGNING_KEY": jwt_secret_key,
    # VERIFYING_KEY not needed for symmetric HS256 (same key signs and verifies)
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "TOKEN_OBTAIN_SERIALIZER": "core.handlers.CustomTokenObtainPairSerializer",
}

CORS_ORIGIN_ALLOW_ALL = True
