"""
Vistas de la app users: listado de usuarios y registro de nuevas cuentas.
La autenticación (login) la maneja directamente simplejwt en config/urls.py.
"""
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status, serializers as drf_serializers
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from .models import Usuario


@extend_schema(
    summary="Listar usuarios (tabla Supabase)",
    description="Devuelve todos los registros de la tabla 'users' de Supabase. No requiere autenticación.",
    responses={
        200: inline_serializer(
            name='UsuarioItem',
            fields={
                'id': drf_serializers.IntegerField(),
                'created_at': drf_serializers.DateTimeField(),
                'name': drf_serializers.CharField(),
                'age': drf_serializers.IntegerField(),
            },
        ),
    },
    tags=['Usuarios'],
)
@api_view(['GET'])
@permission_classes([AllowAny])
def listar_users(request):
    # Devuelve todos los usuarios de la tabla 'users' como JSON.
    users = list(Usuario.objects.all().values('id', 'created_at', 'name', 'age'))
    return Response(users)


@extend_schema(
    summary="Registrar nuevo usuario",
    description="Crea un nuevo usuario en el sistema de auth de Django. No requiere autenticación.",
    request=inline_serializer(
        name='RegisterRequest',
        fields={
            'username': drf_serializers.CharField(),
            'email': drf_serializers.EmailField(required=False),
            'password': drf_serializers.CharField(),
        },
    ),
    responses={
        201: inline_serializer(
            name='RegisterSuccess',
            fields={
                'message': drf_serializers.CharField(),
                'id': drf_serializers.IntegerField(),
            },
        ),
        400: OpenApiResponse(description='Username/password faltantes o ya en uso'),
    },
    tags=['Usuarios'],
)
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
