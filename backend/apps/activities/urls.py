from django.urls import path
from .views import (
    ActivityListCreateView,
    ActivityDetailView,
    SubActivityListCreateView,
    SubActivityDetailView,
)

urlpatterns = [
    # GET  /api/activities/          → lista actividades del usuario
    # POST /api/activities/          → crear actividad (US-01)
    path('', ActivityListCreateView.as_view(), name='activity-list-create'),

    # GET    /api/activities/<id>/   → detalle con subtareas (US-01, US-02)
    # PATCH  /api/activities/<id>/   → editar actividad (US-03)
    # DELETE /api/activities/<id>/   → eliminar actividad (US-03)
    path('<int:pk>/', ActivityDetailView.as_view(), name='activity-detail'),

    # GET  /api/activities/<id>/subtasks/       → listar subtareas (US-02)
    # POST /api/activities/<id>/subtasks/       → crear subtarea (US-02)
    path('<int:activity_pk>/subtasks/', SubActivityListCreateView.as_view(), name='subactivity-list-create'),

    # GET    /api/activities/<id>/subtasks/<id>/  → detalle subtarea
    # PATCH  /api/activities/<id>/subtasks/<id>/  → editar subtarea (US-03)
    # DELETE /api/activities/<id>/subtasks/<id>/  → eliminar subtarea (US-03)
    path('<int:activity_pk>/subtasks/<int:pk>/', SubActivityDetailView.as_view(), name='subactivity-detail'),
]
