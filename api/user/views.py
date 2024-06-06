from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.contrib.auth import login
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.loader import get_template
from drf_spectacular.utils import extend_schema
from rest_framework.authentication import authenticate
from rest_framework.generics import GenericAPIView

from api.config.api import BASE_DIR
from api.user.models import User

if TYPE_CHECKING:
    from rest_framework.request import Request
    from rest_framework.response import Response

logger = logging.getLogger(__name__)


class UserStatsView(GenericAPIView):
    template = get_template(
        (BASE_DIR / "api" / "user" / "templates" / "user" / "stats.html").as_posix(),
    )

    @extend_schema(exclude=True)
    def get(self, request: Request) -> HttpResponse | Response:
        if isinstance(request.user, AnonymousUser):
            return redirect("/login/?next=/webviews/")

        context = {
            "users": User.objects.all(),
        }

        return HttpResponse(
            self.template.render(context, request),
        )


class LoginView(GenericAPIView):
    template = get_template(
        (BASE_DIR / "api" / "user" / "templates" / "user" / "login.html").as_posix(),
    )

    @extend_schema(exclude=True)
    def get(self, request: Request) -> HttpResponse | Response:
        context = {
            request: request,
        }

        return HttpResponse(
            self.template.render(context, request),
        )

    @extend_schema(exclude=True)
    def post(self, request: Request) -> HttpResponse | Response:
        username = request.data["username"]
        password = request.data["password"]

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponse("Authenticated successfully")

            return HttpResponse("Disabled account", status=401)

        return HttpResponse("Invalid login", status=401)
