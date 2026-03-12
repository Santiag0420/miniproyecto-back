from rest_framework import serializers
from django.utils import timezone
from .models import Activity, SubActivity


class SubActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubActivity
        fields = ['id', 'nombre', 'fecha_objetivo', 'horas_estimadas', 'completada']

    def validate_nombre(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("El nombre de la subtarea es obligatorio.")
        return value

    def validate_horas_estimadas(self, value):
        if value <= 0:
            raise serializers.ValidationError("Las horas estimadas deben ser mayores a 0.")
        return value

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


class ActivitySerializer(serializers.ModelSerializer):
    # Las subtareas se incluyen en la respuesta del detalle de la actividad
    subactivities = SubActivitySerializer(many=True, read_only=True)

    class Meta:
        model = Activity
        fields = [
            'id', 'titulo', 'tipo', 'curso', 'descripcion',
            'fecha_evento', 'fecha_limite', 'fecha_creacion',
            'subactivities',
        ]
        read_only_fields = ['fecha_creacion']

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
