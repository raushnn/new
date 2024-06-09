# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/
from __future__ import annotations

from os import environ, getenv
from typing import Any

from storages.backends.s3 import S3Storage

from api.config.api import BASE_DIR

STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_URL = "static/"

AWS_STORAGE_BUCKET_NAME = environ["AWS_STORAGE_BUCKET_NAME"]
_AWS_S3_CUSTOM_DOMAIN = getenv("AWS_S3_CUSTOM_DOMAIN")
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.{_AWS_S3_CUSTOM_DOMAIN}"
AWS_S3_ENDPOINT_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}"

AWS_S3_ACCESS_KEY_ID = environ["AWS_S3_ACCESS_KEY_ID"]
AWS_S3_SECRET_ACCESS_KEY = environ["AWS_S3_SECRET_ACCESS_KEY"]


class CustomDomainS3Storage(S3Storage):
    """Extend S3 with signed URLs for custom domains."""

    custom_domain = False

    def url(
        self,
        name: str,
        parameters: Any = None,
        expire: Any = None,
        http_method: Any = None,
    ) -> str:
        """Replace internal domain with custom domain for signed URLs."""
        url = super().url(name, parameters, expire, http_method)

        return url.replace(
            f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com",
            AWS_S3_ENDPOINT_URL,
        )


STORAGES = {
    "default": {
        "BACKEND": "api.config.storage.CustomDomainS3Storage",
        "OPTIONS": {
            "bucket_name": AWS_STORAGE_BUCKET_NAME,
            "access_key": AWS_S3_ACCESS_KEY_ID,
            "secret_key": AWS_S3_SECRET_ACCESS_KEY,
            "endpoint_url": AWS_S3_ENDPOINT_URL,
        },
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
