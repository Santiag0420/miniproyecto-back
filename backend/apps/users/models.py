from django.db import models
from django.contrib.auth.models import User


class PerfilUsuario(models.Model):
    """
    Perfil extendido del usuario de Django.
    Almacena preferencias del usuario como el límite de horas diarias de trabajo.
    Se crea automáticamente al registrar un nuevo usuario (via signal).
    """
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil'
    )
    limite_horas_diarias = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=6.0,
        help_text='Máximo de horas de trabajo planificadas por día.'
    )

    def __str__(self):
        return f'Perfil de {self.usuario.username} ({self.limite_horas_diarias}h/día)'


class Usuario(models.Model):
    """
    Representa la tabla 'users' que ya existe en Supabase.
    managed=False indica que Django NO crea ni modifica esta tabla con migraciones.
    """
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    name = models.CharField(max_length=100)
    age = models.IntegerField()

    class Meta:
        db_table = 'users'
        managed = False
