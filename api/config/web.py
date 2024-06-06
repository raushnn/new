from __future__ import annotations

from os import getenv
from typing import Any

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = getenv(
    "SECRET_KEY",
    default="django-insecure-2cb-!o^00(qos7$0wf@$ai#h9!^(ov7w6cj%#0ui;o=ulo!83!",
)

ALLOWED_HOSTS = getenv("ALLOWED_HOSTS", "*").split(",")
ALLOWED_HOSTS.append("localhost")

CSRF_TRUSTED_ORIGINS = getenv(
    "CSRF_TRUSTED_ORIGINS",
    "https://core-ai.cdo-global.com,https://test-core-ai.cdo-global.com,https://dev-core-ai.cdo-global.com",
).split(",")

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "api.web.urls"

TEMPLATES: list[dict[str, Any]] = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "api.web.wsgi.application"


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]
