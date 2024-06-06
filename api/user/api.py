from __future__ import annotations

from typing import TYPE_CHECKING

from django.shortcuts import redirect

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


def logout(request: HttpRequest) -> HttpResponse:
    request.session.flush()
    return redirect("/")
