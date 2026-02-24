from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound
from .models import Activity, SubActivity
from .serializers import ActivitySerializer, SubActivitySerializer


class ActivityListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/activities/  → lista las actividades del usuario autenticado (US-01)
    POST /api/activities/  → crea una nueva actividad (US-01)
    El campo 'usuario' se asigna automáticamente desde request.user (JWT).
    """
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Cada usuario solo ve sus propias actividades
        return Activity.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        # Enlaza la actividad al usuario autenticado via JWT
        serializer.save(usuario=self.request.user)


class ActivityDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/activities/<id>/  → detalle de la actividad con sus subtareas (US-01, US-02)
    PATCH  /api/activities/<id>/  → editar campos de la actividad (US-03)
    DELETE /api/activities/<id>/  → eliminar la actividad y sus subtareas (US-03)
    Solo permite acceder a actividades que pertenecen al usuario autenticado.
    """
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Activity.objects.filter(usuario=self.request.user)


class SubActivityListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/activities/<activity_pk>/subtasks/  → lista subtareas de la actividad (US-02)
    POST /api/activities/<activity_pk>/subtasks/  → crea una nueva subtarea (US-02)
    Verifica que la actividad padre pertenezca al usuario autenticado.
    """
    serializer_class = SubActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def _get_activity(self):
        try:
            return Activity.objects.get(
                pk=self.kwargs['activity_pk'],
                usuario=self.request.user
            )
        except Activity.DoesNotExist:
            raise NotFound("Actividad no encontrada.")

    def get_queryset(self):
        activity = self._get_activity()
        return SubActivity.objects.filter(activity=activity)

    def perform_create(self, serializer):
        activity = self._get_activity()
        serializer.save(activity=activity)


class SubActivityDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/activities/<activity_pk>/subtasks/<id>/  → detalle subtarea (US-02)
    PATCH  /api/activities/<activity_pk>/subtasks/<id>/  → editar subtarea (US-03)
    DELETE /api/activities/<activity_pk>/subtasks/<id>/  → eliminar subtarea (US-03)
    """
    serializer_class = SubActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SubActivity.objects.filter(
            activity_id=self.kwargs['activity_pk'],
            activity__usuario=self.request.user
        )
