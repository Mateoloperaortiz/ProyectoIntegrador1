"""
Storage backends for handling static and media files in production.
"""
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    """
    Storage for static files in production using S3.
    """
    location = settings.STATIC_LOCATION
    default_acl = 'public-read'


class MediaStorage(S3Boto3Storage):
    """
    Storage for media files in production using S3.
    """
    location = settings.MEDIA_LOCATION
    default_acl = 'public-read'
    file_overwrite = False
