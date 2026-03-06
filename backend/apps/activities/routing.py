from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/activities/today/', consumers.TodayConsumer.as_asgi()),
]
