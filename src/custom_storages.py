from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


# noinspection PyAbstractClass
class StaticStorage(S3Boto3Storage):
    location = settings.STATICFILES_LOCATION


# noinspection PyAbstractClass
class MediaStorage(S3Boto3Storage):
    location = settings.MEDIAFILES_LOCATION
    file_overwrite = True
