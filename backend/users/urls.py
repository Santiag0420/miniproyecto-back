from django.urls import path
from .views import listar_users

urlpatterns = [
    path('', listar_users),
]
