from django.db import migrations


class Migration(migrations.Migration):
    """
    Migración vacía para apps.users.
    El modelo Usuario tiene managed=False (tabla existente en Supabase),
    por lo que Django no crea ni modifica esa tabla.
    """
    initial = True
    dependencies = []
    operations = []
