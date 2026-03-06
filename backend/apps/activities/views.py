from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Activity, SubActivity
from .serializers import ActivitySerializer, SubActivitySerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.utils import timezone


def _notify_today(user_id):
    """Notifica al WebSocket del usuario que los datos de 'hoy' cambiaron."""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"today_{user_id}",
        {"type": "today.update"},
    )


@extend_schema(
    tags=['Actividades'],
    summary="Vista de hoy: actividades por prioridad",
    description="Devuelve las actividades del usuario agrupadas en vencidas, de hoy y próximas, ordenadas por horas pendientes descendente.",
    responses={
        200: ActivitySerializer(many=True),
        401: OpenApiResponse(description='No autenticado'),
    },
)
class TodayView(APIView):
    """
    Vista 'Hoy': devuelve las actividades del usuario ordenadas por prioridad.
    Orden: Vencidas > Hoy > Próximas. Desempate por horas_estimadas (mayor primero).
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = timezone.localdate()

        activities = Activity.objects.filter(
            usuario=request.user
        ).prefetch_related('subactivities')

        vencidas = []
        hoy = []
        proximas = []

        now = timezone.now()

        for activity in activities:
            # Usar fecha_limite como referencia principal; fecha_evento como fallback
            dt_ref = activity.fecha_limite or activity.fecha_evento

            # Calcular total de horas estimadas de subtareas no completadas
            horas = sum(
                s.horas_estimadas for s in activity.subactivities.all()
                if not s.completada
            )

            fecha_local = timezone.localtime(dt_ref).date() if dt_ref else None

            data = ActivitySerializer(activity).data
            data['horas_pendientes'] = float(horas)
            data['fecha_referencia'] = str(fecha_local) if fecha_local else None

            if dt_ref is None:
                proximas.append(data)
            elif dt_ref < now:
                # El datetime ya pasó → vencida (aunque la fecha sea hoy)
                vencidas.append(data)
            elif fecha_local == today:
                hoy.append(data)
            else:
                proximas.append(data)

        # Vencidas: más antiguas primero (fecha ascendente), None al final
        vencidas.sort(key=lambda x: x['fecha_referencia'] or '9999-12-31')
        # Hoy: más horas pendientes primero
        hoy.sort(key=lambda x: x['horas_pendientes'], reverse=True)
        # Próximas: más cercanas primero (fecha ascendente), None al final
        proximas.sort(key=lambda x: x['fecha_referencia'] or '9999-12-31')

        return Response({
            'vencidas': vencidas,
            'hoy': hoy,
            'proximas': proximas,
        })


@extend_schema(tags=['Actividades'])
class ActivityListCreateView(generics.ListCreateAPIView):
    """
    Lista todas las actividades del usuario autenticado o crea una nueva.
    El campo 'usuario' se asigna automáticamente desde el token JWT,
    garantizando que cada actividad quede enlazada a quien la creó.
    """
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Listar actividades del usuario",
        description="Devuelve todas las actividades del usuario autenticado, incluyendo sus subtareas.",
        responses={200: ActivitySerializer(many=True), 401: OpenApiResponse(description='No autenticado')},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Crear actividad",
        description="Crea una nueva actividad para el usuario autenticado. El campo 'usuario' se asigna automáticamente.",
        responses={
            201: ActivitySerializer,
            400: OpenApiResponse(description='Datos inválidos'),
            401: OpenApiResponse(description='No autenticado'),
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        # Filtra para que cada usuario solo vea sus propias actividades
        return Activity.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)
        _notify_today(self.request.user.id)


@extend_schema(tags=['Actividades'])
class ActivityDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Recupera, edita o elimina una actividad específica del usuario autenticado.
    Al eliminar una actividad, se borran en cascada todas sus subtareas.
    """
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Obtener actividad",
        description="Devuelve el detalle de una actividad junto con todas sus subtareas.",
        responses={
            200: ActivitySerializer,
            401: OpenApiResponse(description='No autenticado'),
            404: OpenApiResponse(description='Actividad no encontrada'),
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Actualizar actividad (completa)",
        responses={
            200: ActivitySerializer,
            400: OpenApiResponse(description='Datos inválidos'),
            401: OpenApiResponse(description='No autenticado'),
            404: OpenApiResponse(description='Actividad no encontrada'),
        },
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="Actualizar actividad (parcial)",
        responses={
            200: ActivitySerializer,
            400: OpenApiResponse(description='Datos inválidos'),
            401: OpenApiResponse(description='No autenticado'),
            404: OpenApiResponse(description='Actividad no encontrada'),
        },
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary="Eliminar actividad",
        description="Elimina la actividad y todas sus subtareas en cascada.",
        responses={
            204: OpenApiResponse(description='Actividad eliminada'),
            401: OpenApiResponse(description='No autenticado'),
            404: OpenApiResponse(description='Actividad no encontrada'),
        },
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def perform_update(self, serializer):
        serializer.save()
        _notify_today(self.request.user.id)

    def perform_destroy(self, instance):
        user_id = self.request.user.id
        instance.delete()
        _notify_today(user_id)

    def get_queryset(self):
        return Activity.objects.filter(usuario=self.request.user)


@extend_schema(tags=['Subtareas'])
class SubActivityListCreateView(generics.ListCreateAPIView):
    """
    Lista las subtareas de una actividad o agrega una nueva.
    Verifica que la actividad padre pertenezca al usuario autenticado
    antes de operar, devolviendo 404 si no existe o no le pertenece.
    """
    serializer_class = SubActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Listar subtareas de una actividad",
        responses={
            200: SubActivitySerializer(many=True),
            401: OpenApiResponse(description='No autenticado'),
            404: OpenApiResponse(description='Actividad no encontrada'),
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Crear subtarea",
        description="Agrega una nueva subtarea a la actividad especificada.",
        responses={
            201: SubActivitySerializer,
            400: OpenApiResponse(description='Datos inválidos'),
            401: OpenApiResponse(description='No autenticado'),
            404: OpenApiResponse(description='Actividad no encontrada'),
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def _get_activity(self):
        try:
            return Activity.objects.get(
                pk=self.kwargs['activity_pk'],
                usuario=self.request.user
            )
        except Activity.DoesNotExist:
            raise NotFound("Actividad no encontrada.")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['activity'] = self._get_activity()
        return context

    def get_queryset(self):
        activity = self._get_activity()
        return SubActivity.objects.filter(activity=activity)

    def perform_create(self, serializer):
        activity = self._get_activity()
        serializer.save(activity=activity)
        _notify_today(self.request.user.id)


@extend_schema(tags=['Subtareas'])
class SubActivityDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Recupera, edita o elimina una subtarea específica.
    Solo accesible si la actividad padre pertenece al usuario autenticado.
    """
    serializer_class = SubActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Obtener subtarea",
        responses={
            200: SubActivitySerializer,
            401: OpenApiResponse(description='No autenticado'),
            404: OpenApiResponse(description='Subtarea no encontrada'),
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Actualizar subtarea (completa)",
        responses={
            200: SubActivitySerializer,
            400: OpenApiResponse(description='Datos inválidos'),
            401: OpenApiResponse(description='No autenticado'),
            404: OpenApiResponse(description='Subtarea no encontrada'),
        },
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="Actualizar subtarea (parcial)",
        responses={
            200: SubActivitySerializer,
            400: OpenApiResponse(description='Datos inválidos'),
            401: OpenApiResponse(description='No autenticado'),
            404: OpenApiResponse(description='Subtarea no encontrada'),
        },
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary="Eliminar subtarea",
        responses={
            204: OpenApiResponse(description='Subtarea eliminada'),
            401: OpenApiResponse(description='No autenticado'),
            404: OpenApiResponse(description='Subtarea no encontrada'),
        },
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def perform_update(self, serializer):
        serializer.save()
        _notify_today(self.request.user.id)

    def perform_destroy(self, instance):
        user_id = self.request.user.id
        instance.delete()
        _notify_today(user_id)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        try:
            context['activity'] = Activity.objects.get(
                pk=self.kwargs['activity_pk'],
                usuario=self.request.user
            )
        except Activity.DoesNotExist:
            pass
        return context

    def get_queryset(self):
        return SubActivity.objects.filter(
            activity_id=self.kwargs['activity_pk'],
            activity__usuario=self.request.user
        )
