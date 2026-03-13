from datetime import timedelta
from decimal import Decimal

from rest_framework import generics, permissions, status
from rest_framework.exceptions import NotFound
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Activity, SubActivity
from .serializers import ActivitySerializer, SubActivitySerializer, SubtareaHoySerializer
from .utils import get_horas_dia, get_sugerencias, verificar_conflicto, generar_sugerencias
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
    summary="Vista de hoy: subtareas agrupadas por fecha",
    description=(
        "Retorna subtareas del usuario agrupadas en overdue/today/upcoming según su fecha_objetivo. "
        "Cada subtarea incluye contexto de la actividad padre. Las subtareas con estado='hecha' no aparecen. "
        "Filtros opcionales: ?curso=, ?estado=, ?upcoming_days= (defecto 7)."
    ),
    responses={
        200: OpenApiResponse(description='Subtareas agrupadas'),
        401: OpenApiResponse(description='No autenticado'),
    },
)
class TodayView(APIView):
    """
    Vista 'Hoy': subtareas agrupadas por su fecha_objetivo.
    - overdue:  fecha_objetivo < hoy
    - today:    fecha_objetivo = hoy
    - upcoming: fecha_objetivo > hoy (hasta upcoming_days días)
    Las subtareas con estado='hecha' no aparecen en ningún grupo.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from django.db.models import Sum
        hoy = timezone.localdate()

        try:
            upcoming_days = int(request.query_params.get('upcoming_days', 7))
        except (ValueError, TypeError):
            upcoming_days = 7

        # Base: subtareas del usuario, excluye las hechas
        base_qs = SubActivity.objects.filter(
            activity__usuario=request.user,
        ).exclude(estado='hecha').select_related('activity')

        filtro_curso = request.query_params.get('curso')
        if filtro_curso:
            base_qs = base_qs.filter(activity__curso=filtro_curso)

        filtro_estado = request.query_params.get('estado')
        if filtro_estado:
            base_qs = base_qs.filter(estado=filtro_estado)

        overdue = base_qs.filter(
            fecha_objetivo__lt=hoy
        ).order_by('fecha_objetivo', 'horas_estimadas')

        today_qs = base_qs.filter(
            fecha_objetivo=hoy
        ).order_by('horas_estimadas')

        upcoming = base_qs.filter(
            fecha_objetivo__gt=hoy,
            fecha_objetivo__lte=hoy + timedelta(days=upcoming_days),
        ).order_by('fecha_objetivo', 'horas_estimadas')

        horas_hoy = today_qs.aggregate(total=Sum('horas_estimadas'))['total'] or 0

        try:
            limite = float(request.user.perfil.limite_horas_diarias)
        except Exception:
            limite = 6.0

        return Response({
            'overdue':   SubtareaHoySerializer(overdue, many=True).data,
            'today':     SubtareaHoySerializer(today_qs, many=True).data,
            'upcoming':  SubtareaHoySerializer(upcoming, many=True).data,
            'summary': {
                'overdue_count':         overdue.count(),
                'today_count':           today_qs.count(),
                'upcoming_count':        upcoming.count(),
                'horas_planificadas_hoy': round(float(horas_hoy), 1),
                'limite_diario':          limite,
                'horas_disponibles_hoy':  round(max(0.0, limite - float(horas_hoy)), 1),
            },
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

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # --- Detección de reprogramación (US-06 / US-07) ---
        nueva_fecha_str = request.data.get('fecha_objetivo')
        forzar = str(request.data.get('forzar', 'false')).lower() in ('true', '1')

        if nueva_fecha_str and not forzar:
            from datetime import date as date_type
            try:
                nueva_fecha = date_type.fromisoformat(str(nueva_fecha_str))
            except (ValueError, TypeError):
                nueva_fecha = None

            # Solo verificar si la fecha realmente cambió
            if nueva_fecha is not None and instance.fecha_objetivo != nueva_fecha:
                # Usar las nuevas horas si el usuario también las cambia (opción reducir)
                nuevas_horas_raw = request.data.get('horas_estimadas')
                horas_para_calculo = (
                    Decimal(str(nuevas_horas_raw))
                    if nuevas_horas_raw is not None
                    else instance.horas_estimadas
                )

                resultado = verificar_conflicto(
                    usuario=request.user,
                    dia=nueva_fecha,
                    horas_subtarea=horas_para_calculo,
                    excluir_subtarea_id=instance.pk,
                )

                if resultado['conflict']:
                    sugerencias = generar_sugerencias(
                        usuario=request.user,
                        dia=nueva_fecha,
                        horas_subtarea=horas_para_calculo,
                        subtarea_id=instance.pk,
                    )
                    return Response({
                        'error': {
                            'code': 'OVERLOAD_CONFLICT',
                            'message': (
                                f"Quedarías con {resultado['planned_hours']:.1f}h "
                                f"planificadas (límite {resultado['daily_limit']:.1f}h)"
                            ),
                            'detail': {
                                'target_date': str(nueva_fecha),
                                'planned_hours': resultado['planned_hours'],
                                'daily_limit': resultado['daily_limit'],
                                'excess_hours': resultado['excess_hours'],
                            },
                            'suggestions': sugerencias,
                        }
                    }, status=status.HTTP_409_CONFLICT)

        # Sin conflicto o forzado → guardar normalmente
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        _notify_today(request.user.id)
        return Response(serializer.data)

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


@extend_schema(
    tags=['Actividades'],
    summary="Carga de trabajo de un día",
    description="Devuelve las horas planificadas para una fecha específica, el límite diario y las subtareas asignadas a ese día.",
    responses={200: OpenApiResponse(description='Carga del día'), 400: OpenApiResponse(description='Fecha inválida')},
)
class DayWorkloadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, fecha):
        from datetime import date as date_type
        try:
            dia = date_type.fromisoformat(str(fecha))
        except (ValueError, TypeError):
            return Response({'error': 'Fecha inválida. Usa formato YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            limite = float(request.user.perfil.limite_horas_diarias)
        except Exception:
            limite = 6.0

        subtareas = SubActivity.objects.filter(
            activity__usuario=request.user,
            fecha_objetivo=dia,
        ).exclude(estado='hecha').select_related('activity')

        horas_planificadas = float(sum(s.horas_estimadas for s in subtareas))

        return Response({
            'fecha': str(dia),
            'horas_planificadas': round(horas_planificadas, 1),
            'limite_diario': limite,
            'horas_disponibles': round(max(0.0, limite - horas_planificadas), 1),
            'sobrecargado': horas_planificadas > limite,
            'subtareas': [
                {
                    'id': s.id,
                    'nombre': s.nombre,
                    'horas_estimadas': float(s.horas_estimadas),
                    'estado': s.estado,
                    'actividad_id': s.activity_id,
                    'actividad_titulo': s.activity.titulo,
                }
                for s in subtareas
            ],
        })
