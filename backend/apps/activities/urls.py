from django.urls import path
from .views import (
    ActivityListCreateView,
    ActivityDetailView,
    SubActivityListCreateView,
    SubActivityDetailView,
    TodayView,
    DayWorkloadView,
)

urlpatterns = [
    path('', ActivityListCreateView.as_view(), name='activity-list-create'),
    path('<int:pk>/', ActivityDetailView.as_view(), name='activity-detail'),
    path('<int:activity_pk>/subtasks/', SubActivityListCreateView.as_view(), name='subactivity-list-create'),
    path('<int:activity_pk>/subtasks/<int:pk>/', SubActivityDetailView.as_view(), name='subactivity-detail'),
    path('today/', TodayView.as_view(), name='today'),
    path('days/<str:fecha>/workload/', DayWorkloadView.as_view(), name='day-workload'),
]
