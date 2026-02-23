"""
Router principal de URLs del proyecto.
Agrupa todas las rutas: admin, API de usuarios y autenticación JWT.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


def home(request):
    # Endpoint raíz para verificar que la API está activa.
    return JsonResponse({'message': 'Bienvenido a la API'})


urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),

    # Rutas de la app users: listar usuarios y registrar nuevos.
    path('api/users/', include('apps.users.urls')),

    # Autenticación JWT: login devuelve access + refresh token.
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    # Renueva el access token usando el refresh token.
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
