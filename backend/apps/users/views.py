"""
Vistas de la app users: listado de usuarios y registro de nuevas cuentas.
La autenticación (login) la maneja directamente simplejwt en config/urls.py.
"""
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, serializers as drf_serializers
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from .models import Usuario, PerfilUsuario


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


def _perfil_data(user, perfil):
    return {
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'date_joined': user.date_joined.date().isoformat(),
        'limite_horas_diarias': float(perfil.limite_horas_diarias),
    }


@extend_schema(
    summary="Ver o actualizar perfil del usuario",
    description=(
        "GET devuelve los datos del perfil (username, email, nombres, límite diario). "
        "PATCH permite actualizar cualquiera de esos campos."
    ),
    request=inline_serializer(
        name='PerfilRequest',
        fields={
            'username': drf_serializers.CharField(required=False),
            'email': drf_serializers.EmailField(required=False),
            'first_name': drf_serializers.CharField(required=False),
            'last_name': drf_serializers.CharField(required=False),
            'limite_horas_diarias': drf_serializers.FloatField(required=False),
        },
    ),
    responses={
        200: inline_serializer(
            name='PerfilResponse',
            fields={
                'username': drf_serializers.CharField(),
                'email': drf_serializers.EmailField(),
                'first_name': drf_serializers.CharField(),
                'last_name': drf_serializers.CharField(),
                'date_joined': drf_serializers.DateField(),
                'limite_horas_diarias': drf_serializers.FloatField(),
            },
        ),
        400: OpenApiResponse(description='Datos inválidos'),
    },
    tags=['Usuarios'],
)
@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def perfil_view(request):
    """Devuelve o actualiza el perfil del usuario autenticado."""
    user = request.user
    perfil, _ = PerfilUsuario.objects.get_or_create(usuario=user)

    if request.method == 'GET':
        return Response(_perfil_data(user, perfil))

    # PATCH — todos los campos son opcionales
    data = request.data

    if 'username' in data:
        nuevo_username = data['username'].strip()
        if not nuevo_username:
            return Response({'error': 'El username no puede estar vacío.'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=nuevo_username).exclude(pk=user.pk).exists():
            return Response({'error': 'El nombre de usuario ya está en uso.'}, status=status.HTTP_400_BAD_REQUEST)
        user.username = nuevo_username

    if 'email' in data:
        nuevo_email = data['email'].strip()
        if nuevo_email and User.objects.filter(email=nuevo_email).exclude(pk=user.pk).exists():
            return Response({'error': 'El email ya está registrado.'}, status=status.HTTP_400_BAD_REQUEST)
        user.email = nuevo_email

    if 'first_name' in data:
        user.first_name = data['first_name'].strip()

    if 'last_name' in data:
        user.last_name = data['last_name'].strip()

    if 'limite_horas_diarias' in data:
        try:
            limite = float(data['limite_horas_diarias'])
            if not (1 <= limite <= 16):
                raise ValueError
        except (ValueError, TypeError):
            return Response({'error': 'El límite debe ser un número entre 1 y 16.'}, status=status.HTTP_400_BAD_REQUEST)
        perfil.limite_horas_diarias = limite
        perfil.save()

    user.save()
    return Response(_perfil_data(user, perfil))


@extend_schema(
    summary="Cambiar contraseña",
    description="Verifica la contraseña actual y la reemplaza por la nueva.",
    request=inline_serializer(
        name='ChangePasswordRequest',
        fields={
            'current_password': drf_serializers.CharField(),
            'new_password': drf_serializers.CharField(),
        },
    ),
    responses={
        200: inline_serializer(
            name='ChangePasswordResponse',
            fields={'message': drf_serializers.CharField()},
        ),
        400: OpenApiResponse(description='Contraseña actual incorrecta o nueva inválida'),
    },
    tags=['Usuarios'],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Cambia la contraseña del usuario autenticado."""
    current = request.data.get('current_password', '')
    new = request.data.get('new_password', '')

    if not current or not new:
        return Response(
            {'error': 'current_password y new_password son requeridos.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not request.user.check_password(current):
        return Response(
            {'error': 'La contraseña actual no es correcta.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(new) < 6:
        return Response(
            {'error': 'La nueva contraseña debe tener al menos 6 caracteres.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    request.user.set_password(new)
    request.user.save()
    return Response({'message': 'Contraseña actualizada correctamente.'})
