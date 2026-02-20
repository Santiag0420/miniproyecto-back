from django.db import models

class Usuario(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    name = models.CharField(max_length=100)
    age = models.IntegerField()

    class Meta:
        db_table = 'users'  
        managed = False         
