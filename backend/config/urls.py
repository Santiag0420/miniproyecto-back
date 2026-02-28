"""
Router principal de URLs del proyecto.
Agrupa todas las rutas: admin, API de usuarios, autenticación JWT y documentación.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView


def home(request):
    # Endpoint raíz para verificar que la API está activa.
    return JsonResponse({'message': 'Bienvenido a la API'})


urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),

    # Rutas de la app users: listar usuarios y registrar nuevos.
    path('api/users/', include('backend.apps.users.urls')),

    # Rutas de actividades y subtareas.
    path('api/activities/', include('backend.apps.activities.urls')),

    # Autenticación JWT: login devuelve access + refresh token.
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    # Renueva el access token usando el refresh token.
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Documentación de la API — esquema OpenAPI en formato JSON/YAML
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # Swagger UI — interfaz visual interactiva para probar los endpoints
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # ReDoc — vista alternativa de la documentación más legible
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
