from __future__ import annotations

from os import environ, getenv

import dj_database_url

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


def _get_database_url() -> str:
    if "POSTGRES_HOST" not in environ:
        return environ.get("DATABASE_URL", "sqlite:///db.sqlite3")

    postgres_host = environ["POSTGRES_HOST"]
    postgres_port = environ.get("POSTGRES_PORT", "5432")
    postgres_user = environ["POSTGRES_USER"]
    postgres_password = environ["POSTGRES_PASSWORD"]
    postgres_db = environ["POSTGRES_DB"]

    return f"postgres://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"


DATABASE_URL = _get_database_url()
CONN_MAX_AGE = int(getenv("CONN_MAX_AGE", default="600"))

DATABASES = {
    "default": dj_database_url.parse(DATABASE_URL, conn_max_age=CONN_MAX_AGE),
}
