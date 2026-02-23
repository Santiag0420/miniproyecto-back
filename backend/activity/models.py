from django.db import models
from users.models import Usuario
class Activity(models.Model):
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='activities',
        null=True,
        blank=True
    )
    class TipoActividad(models.TextChoices):
        EXAM = "exam", "📝 Examen"
        QUIZ = "quiz", "🧠 Quiz"
        WORKSHOP = "workshop", "🔧 Taller"
        PROJECT = "project", "🚀 Proyecto"
        OTHER = "other", "📌 Otro"
        
    tipo = models.CharField(
        max_length=20,
        choices=TipoActividad.choices,
        default=TipoActividad.OTHER
    )
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    curso = models.CharField(max_length=255, blank=True, null=False)

    def __str__(self):
        return self.titulo


class SubActivity(models.Model):
    activity = models.ForeignKey(
        Activity,
        related_name='subactivities',
        on_delete=models.CASCADE
    )
    nombre = models.CharField(max_length=255)
    completada = models.BooleanField(default=False)
    fecha_objetivo = models.DateField()

    def __str__(self):
        return self.nombre