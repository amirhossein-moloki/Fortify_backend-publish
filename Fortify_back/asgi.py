# اطمینان از بارگذاری کامل تنظیمات Django
import django
django.setup()

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from chats import consumers  # فرض بر این است که شما از این Consumer برای WebSocket استفاده می‌کنید

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Fortify_back.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # پیکربندی برای درخواست‌های HTTP
    "websocket": AuthMiddlewareStack(  # استفاده از AuthMiddlewareStack برای WebSocket
        URLRouter([
            path('ws/chat/<int:chat_id>/', consumers.ChatConsumer.as_asgi()),  # آدرس WebSocket
        ])
    ),
})
