from django.shortcuts import render
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets
from .models import Activity, SubActivity
from .serializers import ActivitySerializer, SubActivitySerializer

class ActivityPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50

class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.all().order_by('-fecha_creacion')
    serializer_class = ActivitySerializer
    pagination_class = ActivityPagination


class SubActivityViewSet(viewsets.ModelViewSet):
    queryset = SubActivity.objects.all()
    serializer_class = SubActivitySerializer