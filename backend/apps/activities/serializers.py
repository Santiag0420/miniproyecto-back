from rest_framework import serializers
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


class ActivitySerializer(serializers.ModelSerializer):
    # Subtareas anidadas — solo lectura; se crean por su propio endpoint
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

    def validate_curso(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("El curso es obligatorio.")
        return value
