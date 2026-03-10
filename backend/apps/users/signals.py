from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import PerfilUsuario


@receiver(post_save, sender=User)
def crear_perfil(sender, instance, created, **kwargs):
    """Crea automáticamente un PerfilUsuario cada vez que se registra un usuario nuevo."""
    if created:
        PerfilUsuario.objects.create(usuario=instance)
