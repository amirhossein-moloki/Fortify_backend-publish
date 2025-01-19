import django
django.setup()


from django.urls import re_path
from .consumers import AccountStatusConsumer

websocket_urlpatterns = [
    re_path(r'^ws/status/(?P<username>\w+)/$', AccountStatusConsumer.as_asgi()),
]
