from __future__ import annotations

from os import getenv

LOG_LEVEL = getenv("LOG_LEVEL", default="INFO")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(asctime)s %(log_color)s%(levelname)s %(name)s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(log_color)s%(levelname)s %(name)s %(message)s",
        },
        "file": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "console_simple": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file_info": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/info.log",
            "maxBytes": 1024 * 1024 * 10,  # 10 MB
            "backupCount": 10,
            "formatter": "file",
        },
        "file_warning": {
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/warning.log",
            "maxBytes": 1024 * 1024 * 10,  # 10 MB
            "backupCount": 10,
            "formatter": "file",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console", "file_info", "file_warning"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "openai": {
            "handlers": ["console_simple", "file_info", "file_warning"],
            "level": "WARNING",
            "propagate": False,
        },
        "pdfminer": {
            "handlers": ["console_simple", "file_info", "file_warning"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}
