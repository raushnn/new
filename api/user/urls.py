from __future__ import annotations

from django.urls import path

from api.user import api, views

urlpatterns = [
    path("api/v1/auth/logout/", api.logout, name="logout"),
    path("login/", views.LoginView.as_view(), name="login"),
]
