from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound
from .models import Activity, SubActivity
from .serializers import ActivitySerializer, SubActivitySerializer


class ActivityListCreateView(generics.ListCreateAPIView):
    """
    Lista todas las actividades del usuario autenticado o crea una nueva.
    El campo 'usuario' se asigna automáticamente desde el token JWT,
    garantizando que cada actividad quede enlazada a quien la creó.
    """
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filtra para que cada usuario solo vea sus propias actividades
        return Activity.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class ActivityDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Recupera, edita o elimina una actividad específica del usuario autenticado.
    Al eliminar una actividad, se borran en cascada todas sus subtareas.
    """
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Activity.objects.filter(usuario=self.request.user)


class SubActivityListCreateView(generics.ListCreateAPIView):
    """
    Lista las subtareas de una actividad o agrega una nueva.
    Verifica que la actividad padre pertenezca al usuario autenticado
    antes de operar, devolviendo 404 si no existe o no le pertenece.
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
    Recupera, edita o elimina una subtarea específica.
    Solo accesible si la actividad padre pertenece al usuario autenticado.
    """
    serializer_class = SubActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SubActivity.objects.filter(
            activity_id=self.kwargs['activity_pk'],
            activity__usuario=self.request.user
        )
