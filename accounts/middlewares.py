import jwt
from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.auth.models import User
from urllib.parse import parse_qs
from channels.exceptions import DenyConnection


class JWTAuthMiddleware:
    """
    Middleware to authenticate WebSocket requests with JWT token.
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # ابتدا بررسی هدر Authorization برای توکن
        token = None
        for header in scope.get('headers', []):
            if header[0] == b'authorization':
                token = header[1].decode().split(' ')[1]
                break

        # اگر توکن در هدر نباشد، از URL استخراج می‌کنیم
        if not token:
            query_params = parse_qs(scope.get('query_string').decode())
            token = query_params.get('token', [None])[0]

        # اگر توکن موجود باشد، آن را اعتبارسنجی می‌کنیم
        if token:
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                user = await self.get_user(payload['user_id'])
                scope['user'] = user  # اضافه کردن کاربر به scope
            except jwt.ExpiredSignatureError:
                await send({
                    "type": "websocket.close",
                    "code": 4000  # کد 4000 نشان‌دهنده مشکل توکن منقضی‌شده است
                })
                raise DenyConnection("Token has expired.")
            except jwt.InvalidTokenError:
                await send({
                    "type": "websocket.close",
                    "code": 4000  # کد 4000 برای توکن نامعتبر
                })
                raise DenyConnection("Invalid token.")
        else:
            await send({
                "type": "websocket.close",
                "code": 4000  # در صورتی که هیچ توکنی وجود نداشته باشد
            })
            raise DenyConnection("No token provided.")

        return await self.inner(scope, receive, send)

    @database_sync_to_async
    def get_user(self, user_id):
        """ دریافت کاربر از ID """
        return User.objects.get(id=user_id)
