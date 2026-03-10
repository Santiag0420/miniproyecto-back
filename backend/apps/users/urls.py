"""
URLs de la app users. Se montan bajo el prefijo /api/users/ definido en config/urls.py.
"""
from django.urls import path
from .views import listar_users, register, perfil_view, change_password

urlpatterns = [
    path('', listar_users),                    # GET  /api/users/
    path('register/', register),               # POST /api/users/register/
    path('profile/', perfil_view),             # GET/PATCH /api/users/profile/
    path('change-password/', change_password), # POST /api/users/change-password/
]
