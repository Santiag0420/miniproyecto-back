"""
URLs de la app users. Se montan bajo el prefijo /api/users/ definido en config/urls.py.
"""
from django.urls import path
from .views import listar_users, register

urlpatterns = [
    path('', listar_users),          # GET  /api/users/        → lista de usuarios
    path('register/', register),     # POST /api/users/register/ → crear cuenta
]
