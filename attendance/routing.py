from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Add your websocket URL patterns here
    # Example: re_path(r'ws/attendance/(?P<room_name>\w+)/$', consumers.AttendanceConsumer.as_asgi()),
]