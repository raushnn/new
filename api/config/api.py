from __future__ import annotations

import sys
from distutils.util import strtobool
from os import getenv
from pathlib import Path

# Application definition
INSTALLED_APPS: list[str] = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_object_actions",
    "import_export",
    "django_ace",
    "rest_framework",
    "drf_spectacular",
    "api.user",
    "api.ai",
]

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = strtobool(getenv("DEBUG", default="False"))

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/
LANGUAGE_CODE = "ru-ru"

TIME_ZONE = getenv("TIME_ZONE", default="UTC")
USE_I18N = strtobool(getenv("USE_I18N", default="True"))
USE_TZ = strtobool(getenv("USE_TZ", default="True"))

APPEND_SLASH = True

AUTH_USER_MODEL = "user.User"

SEND_REAL_AI_REQUESTS = strtobool(getenv("SEND_REAL_AI_REQUESTS", default="True"))

IS_IN_MIGRATION = "makemigrations" in sys.argv or "migrate" in sys.argv
