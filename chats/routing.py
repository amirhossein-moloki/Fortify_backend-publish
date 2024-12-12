import django
django.setup()



import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from .middleware import JWTAuthMiddleware  # اضافه کردن JWTAuthMiddleware
from chats import consumers
from django.urls import path

# اطمینان از راه‌اندازی Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project.settings")


# URL های WebSocket
websocket_urlpatterns = [
    path('ws/chat/<int:chat_id>/', consumers.ChatConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware(  # اضافه کردن Middleware به WebSocket
        AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        )
    ),
})
