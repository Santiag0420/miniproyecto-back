from django.db import models
from django.contrib.auth.models import User


class Activity(models.Model):
    """
    Actividad evaluativa creada por un estudiante.
    Se enlaza al usuario autenticado de Django (auth.User), el mismo que
    maneja el login y los tokens JWT. Los campos fecha_evento y fecha_limite
    son opcionales según el tipo de actividad.
    """
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activities'
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
    # Fecha y hora del evento (examen, quiz, entrega presencial, etc.)
    fecha_evento = models.DateTimeField(null=True, blank=True)
    # Fecha límite para entregar o completar la actividad
    fecha_limite = models.DateField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo


class SubActivity(models.Model):
    """
    Subtarea que divide el trabajo de una actividad en pasos concretos.
    Permite estimar el tiempo necesario y hacer seguimiento del avance
    mediante el campo completada.
    """
    activity = models.ForeignKey(
        Activity,
        related_name='subactivities',
        on_delete=models.CASCADE
    )
    nombre = models.CharField(max_length=255)
    fecha_objetivo = models.DateField()
    # Tiempo estimado para completar esta subtarea (acepta decimales, ej: 1.5)
    horas_estimadas = models.DecimalField(max_digits=5, decimal_places=1)
    completada = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre
