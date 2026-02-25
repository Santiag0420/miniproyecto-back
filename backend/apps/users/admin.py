from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Usuario


# Desregistra el User de auth para reemplazarlo con una versión personalizada
admin.site.unregister(User)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    CRUD completo del modelo User de Django en el panel de administración.
    Solo accesible para usuarios con permisos de staff o superusuario.
    Hereda toda la funcionalidad de BaseUserAdmin (crear, editar, cambiar
    contraseña, activar/desactivar, asignar permisos y grupos).
    """
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    """
    Vista de solo lectura de la tabla 'users' de Supabase.
    No permite crear ni eliminar registros porque la tabla es managed=False.
    """
    list_display = ['id', 'name', 'age', 'created_at']
    search_fields = ['name']
    readonly_fields = ['id', 'name', 'age', 'created_at']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
