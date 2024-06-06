from __future__ import annotations

import os

import django
import django_stubs_ext

django_stubs_ext.monkeypatch()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.config.settings")
django.setup()
