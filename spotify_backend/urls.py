from django.urls import path, include
from . import views

urlpatterns = [
    path("login/", views.login, name="spotify-login"),
    path("login/callback", views.loginCallback, name="spotify-callback"),
]
