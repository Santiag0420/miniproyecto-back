from rest_framework import serializers
from django.utils import timezone
from .models import Activity, SubActivity


class SubActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubActivity
        fields = ['id', 'nombre', 'fecha_objetivo', 'horas_estimadas', 'estado', 'nota_posposicion']

    def validate_nombre(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("El nombre de la subtarea es obligatorio.")
        return value

    def validate_horas_estimadas(self, value):
        if value <= 0:
            raise serializers.ValidationError("Las horas estimadas deben ser mayores a 0.")
        return value

    def validate_estado(self, value):
        valores_validos = [e.value for e in SubActivity.EstadoSubtarea]
        if value not in valores_validos:
            raise serializers.ValidationError(
                f"Estado no válido. Usa: {', '.join(valores_validos)}."
            )
        return value

    def validate(self, data):
        # Al posponer se puede incluir nota; al marcar hecha se limpia la nota
        if data.get('estado') == 'hecha':
            data['nota_posposicion'] = None
        return data

    def validate_fecha_objetivo(self, value):
        # Obtiene la actividad desde el contexto (inyectada por la vista)
        # o desde la instancia existente (en caso de actualización).
        activity = self.context.get('activity')
        if activity is None and self.instance:
            activity = self.instance.activity

        if activity is None:
            return value

        # ← Usar localtime() para convertir a zona horaria local antes de .date()
        from django.utils import timezone as tz
        inicio = tz.localtime(activity.fecha_evento).date() if activity.fecha_evento else None
        fin = tz.localtime(activity.fecha_limite).date() if activity.fecha_limite else None

        if inicio and value < inicio:
            raise serializers.ValidationError(
                f"La fecha objetivo ({value}) no puede ser anterior "
                f"a la fecha del evento ({inicio})."
            )
        if fin and value > fin:
            raise serializers.ValidationError(
                f"La fecha objetivo ({value}) no puede ser posterior "
                f"a la fecha límite ({fin})."
            )
        return value


class ActividadResumenSerializer(serializers.ModelSerializer):
    """Contexto mínimo de la actividad padre para anidar en cada subtarea de la vista Hoy."""
    class Meta:
        model = Activity
        fields = ['id', 'titulo', 'curso', 'tipo']


class SubtareaHoySerializer(serializers.ModelSerializer):
    """Subtarea con actividad padre anidada como contexto (solo lectura, para TodayView)."""
    activity = ActividadResumenSerializer(read_only=True)

    class Meta:
        model = SubActivity
        fields = [
            'id', 'nombre', 'fecha_objetivo', 'horas_estimadas',
            'estado', 'nota_posposicion', 'activity',
        ]


class ActivitySerializer(serializers.ModelSerializer):
    subactivities = SubActivitySerializer(many=True, read_only=True)
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = [
            'id', 'titulo', 'tipo', 'curso', 'descripcion',
            'fecha_evento', 'fecha_limite', 'fecha_creacion',
            'subactivities', 'progress',
        ]
        read_only_fields = ['fecha_creacion']

    def get_progress(self, obj):
        subtareas = obj.subactivities.all()
        total = len(subtareas)
        hechas = sum(1 for s in subtareas if s.estado == 'hecha')
        pospuestas = sum(1 for s in subtareas if s.estado == 'pospuesta')
        pendientes = total - hechas - pospuestas
        porcentaje = round((hechas / total) * 100, 1) if total > 0 else 0.0
        return {
            'total': total,
            'hechas': hechas,
            'pendientes': pendientes,
            'pospuestas': pospuestas,
            'porcentaje': porcentaje,
        }

    def validate_titulo(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("El título es obligatorio.")
        return value

    def validate_fecha_evento(self, value):
        if value and value.date() < timezone.localdate():
            raise serializers.ValidationError(
                "La fecha del evento no puede ser en el pasado."
            )
        return value

    def validate_fecha_limite(self, value):
        if value and value.date() < timezone.localdate():
            raise serializers.ValidationError(
                "La fecha límite no puede ser en el pasado."
            )
        return value
