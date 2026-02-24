"""
Vistas de la app users: listado de usuarios y registro de nuevas cuentas.
La autenticación (login) la maneja directamente simplejwt en config/urls.py.
"""
from django.http import JsonResponse
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Usuario


def listar_users(request):
    # Devuelve todos los usuarios de la tabla 'users' como JSON.
    users = Usuario.objects.all().values('id', 'created_at', 'name', 'age')
    return JsonResponse(list(users), safe=False)


@api_view(['POST'])
@permission_classes([AllowAny])  # Permite acceso sin estar autenticado (registro público).
def register(request):
    """
    Crea un nuevo usuario en el sistema de auth de Django.
    Valida que username y password estén presentes y que no existan duplicados.
    """
    username = request.data.get('username')
    email = request.data.get('email', '')
    password = request.data.get('password')

    # Campos obligatorios
    if not username or not password:
        return Response(
            {'error': 'Username y password son requeridos'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Unicidad de username
    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'El nombre de usuario ya está en uso'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Unicidad de email (solo si se proporcionó)
    if email and User.objects.filter(email=email).exists():
        return Response(
            {'error': 'El email ya está registrado'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # create_user hashea la contraseña automáticamente (nunca guardar texto plano).
    user = User.objects.create_user(username=username, email=email, password=password)
    return Response(
        {'message': 'Usuario registrado exitosamente', 'id': user.id},
        status=status.HTTP_201_CREATED
    )
