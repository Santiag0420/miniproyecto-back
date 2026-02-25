from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Crea el superusuario admin con contraseña admin si no existe'

    def handle(self, *args, **options):
        if User.objects.filter(username='admin').exists():
            self.stdout.write(self.style.WARNING('El usuario admin ya existe, no se realizaron cambios.'))
            return

        User.objects.create_superuser(
            username='admin',
            email='admin@admin.com',
            password='admin'
        )
        self.stdout.write(self.style.SUCCESS('Superusuario admin creado — usuario: admin / contraseña: admin'))
