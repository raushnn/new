from __future__ import annotations

from typing import Literal

from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication


class JWTOrSessionAuthenticationMixin(GenericAPIView):
    auth_type: Literal["JWT", "SESSION"] | None = None

    def get_authenticators(self) -> list:
        if not self.request:
            return super().get_authenticators()

        if "Authorization" in self.request.headers:
            self.auth_type = "JWT"
            return [JWTAuthentication()]

        self.auth_type = "SESSION"
        return super().get_authenticators()
