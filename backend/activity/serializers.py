from rest_framework import serializers
from .models import Activity, SubActivity


class SubActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubActivity
        fields = '__all__'


class ActivitySerializer(serializers.ModelSerializer):
    subactivities = SubActivitySerializer(many=True, read_only=True)

    class Meta:
        model = Activity
        fields = '__all__'