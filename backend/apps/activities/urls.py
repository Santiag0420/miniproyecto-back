from django.urls import path
from .views import (
    ActivityListCreateView,
    ActivityDetailView,
    SubActivityListCreateView,
    SubActivityDetailView,
)

urlpatterns = [
    # Listado y creación de actividades del usuario autenticado
    path('', ActivityListCreateView.as_view(), name='activity-list-create'),

    # Detalle, edición y eliminación de una actividad junto con sus subtareas
    path('<int:pk>/', ActivityDetailView.as_view(), name='activity-detail'),

    # Listado y creación de subtareas dentro de una actividad específica
    path('<int:activity_pk>/subtasks/', SubActivityListCreateView.as_view(), name='subactivity-list-create'),

    # Detalle, edición y eliminación de una subtarea específica
    path('<int:activity_pk>/subtasks/<int:pk>/', SubActivityDetailView.as_view(), name='subactivity-detail'),
]
