from django.db import models


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
