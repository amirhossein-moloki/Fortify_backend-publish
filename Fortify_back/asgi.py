# اطمینان از بارگذاری کامل تنظیمات Django
import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from chats import consumers as chat_consumers  # Consumer برای چت
from accounts import consumers as status_consumers  # Consumer برای وضعیت کاربران

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Fortify_back.settings')
django.setup()

# تعریف برنامه ASGI
application = ProtocolTypeRouter({
    # مدیریت درخواست‌های HTTP
    "http": get_asgi_application(),

    # مدیریت ارتباطات WebSocket
    "websocket": AuthMiddlewareStack(
        URLRouter([
            # مسیر WebSocket برای چت
            path('ws/chat/<int:chat_id>/', chat_consumers.ChatConsumer.as_asgi(), name="chat_websocket"),

            # مسیر WebSocket برای وضعیت کاربران
            path('ws/status/', status_consumers.StatusConsumer.as_asgi(), name="status_websocket"),
        ])
    ),
})
