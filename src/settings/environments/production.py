import os

from settings.components import config
from settings.components.base import DATABASES

ALLOWED_HOSTS = ["operationcode.org", "pybot.operationcode.org"]
DEBUG = False

if config("EXTRA_HOSTS", default=""):
    ALLOWED_HOSTS += [s.strip() for s in os.environ["EXTRA_HOSTS"].split(",")]

try:
    import socket

    local_ip = str(socket.gethostbyname(socket.gethostname()))
    ALLOWED_HOSTS.append(local_ip)
except Exception as ex:  # pragma: no cover
    print(ex)


DATABASES = {
    "default": {
        **DATABASES["default"],
        "ENGINE": config("DB_ENGINE", default="django.db.backends.postgresql"),
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = config("BUCKET_REGION_NAME")  # e.g. us-east-2
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
AWS_DEFAULT_ACL = None
AWS_LOCATION = "static"
STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/"
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"
STATICFILES_LOCATION = "static"
MEDIAFILES_LOCATION = "media"
STATICFILES_STORAGE = "custom_storages.StaticStorage"
DEFAULT_FILE_STORAGE = "custom_storages.MediaStorage"
