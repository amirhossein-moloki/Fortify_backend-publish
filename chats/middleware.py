import jwt
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.conf import settings
from channels.auth import BaseMiddleware
from urllib.parse import parse_qs


class JWTAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        super().__init__(inner)

    async def __call__(self, scope, receive, send):
        token = self.get_token(scope)
        user = None

        if token:
            try:
                # دیکد کردن توکن JWT
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user = await self.get_user(payload.get('user_id'))
            except jwt.ExpiredSignatureError:
                # توکن منقضی شده است
                user = None
            except jwt.DecodeError:
                # توکن نامعتبر است
                user = None
            except get_user_model().DoesNotExist:
                # کاربر پیدا نشد
                user = None
        else:
            # کاربر ناشناس
            user = await self.get_anonymous_user()

        # اضافه کردن کاربر به scope
        scope['user'] = user

        # فراخوانی middleware بعدی
        await super().__call__(scope, receive, send)

    def get_token(self, scope):
        """استخراج توکن از URL یا هدر Authorization"""
        # تلاش برای دریافت توکن از query string
        token = parse_qs(scope.get('query_string', b'').decode()).get('token', [None])[0]

        if not token:
            # تلاش برای دریافت توکن از هدر Authorization
            headers = dict(scope.get('headers', {}))
            authorization_header = headers.get(b'authorization', None)

            if authorization_header:
                # Bearer <token>
                try:
                    token = authorization_header.decode().split(' ')[1]
                except IndexError:
                    token = None
        return token

    @database_sync_to_async
    def get_user(self, user_id):
        """دریافت کاربر از دیتابیس"""
        try:
            return get_user_model().objects.filter(id=user_id).first()
        except get_user_model().DoesNotExist:
            return None

    @database_sync_to_async
    def get_anonymous_user(self):
        """ایجاد یا بازیابی یک کاربر ناشناس"""
        # ایجاد یا بازگشت به یک کاربر پیش‌فرض ناشناس
        return None
