from django.db import models
from apps.users.models import Usuario


class Activity(models.Model):
    """
    Representa una actividad evaluativa (US-01).
    Campos obligatorios: titulo, tipo, curso.
    Campos opcionales: descripcion, fecha_evento, fecha_limite.
    """
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='activities',
        null=True,
        blank=True
    )

    class TipoActividad(models.TextChoices):
        EXAM = 'exam', 'Examen'
        QUIZ = 'quiz', 'Quiz'
        WORKSHOP = 'workshop', 'Taller'
        PROJECT = 'project', 'Proyecto'
        OTHER = 'other', 'Otro'

    tipo = models.CharField(
        max_length=20,
        choices=TipoActividad.choices,
        default=TipoActividad.OTHER
    )
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    curso = models.CharField(max_length=255)
    # Fecha y hora en que ocurre el evento (examen, entrega, etc.) — opcional (US-01)
    fecha_evento = models.DateTimeField(null=True, blank=True)
    # Fecha límite de entrega — opcional (US-01)
    fecha_limite = models.DateField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo


class SubActivity(models.Model):
    """
    Subtarea asociada a una actividad (US-02).
    Campos obligatorios: nombre, fecha_objetivo, horas_estimadas (> 0).
    """
    activity = models.ForeignKey(
        Activity,
        related_name='subactivities',
        on_delete=models.CASCADE
    )
    nombre = models.CharField(max_length=255)
    fecha_objetivo = models.DateField()
    # Horas estimadas para completar la subtarea — entero o decimal simple (US-02)
    horas_estimadas = models.DecimalField(max_digits=5, decimal_places=1)
    completada = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre
