import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils.timezone import now
import jwt
from django.conf import settings
from urllib.parse import parse_qs
from .models import User  # وارد کردن مدل User پیش‌فرض

class AccountStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.username = self.scope['url_route']['kwargs'].get('username')

        # بررسی توکن JWT از URL و اعتبارسنجی آن
        token = self.scope.get('query_string', None)
        if token:
            token = parse_qs(token.decode()).get('token', [None])[0]
            if token:
                try:
                    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                    user_id = payload.get('user_id')
                    self.user = await self.get_user(user_id)

                    # اگر کاربر پیدا شد، به‌روزرسانی وضعیت آنلاین و قبول اتصال
                    if self.user:
                        await self.update_user_status(is_online=True)
                        await self.accept()
                        return
                except jwt.ExpiredSignatureError:
                    print("Token has expired.")
                except jwt.InvalidTokenError:
                    print("Invalid token.")

        # اگر توکن معتبر نباشد یا کاربر پیدا نشود، اتصال را ببندید
        await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'user'):
            # به‌روزرسانی وضعیت آفلاین
            await self.update_user_status(is_online=False)

    async def receive(self, text_data):
        """
        دریافت داده‌های ورودی از کلاینت و پردازش آن.
        """
        try:
            data = json.loads(text_data)
            message = data.get("message", "No message received.")

            # ارسال پاسخ به کلاینت
            await self.send(text_data=json.dumps({
                "message": f"Received: {message}",
                "username": self.username  # اضافه کردن username به پاسخ
            }))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                "error": "Invalid JSON format"
            }))

    @database_sync_to_async
    def get_user(self, user_id):
        """ دریافت کاربر از ID """
        return User.objects.get(id=user_id)

    @database_sync_to_async
    def update_user_status(self, is_online):
        """ به‌روزرسانی وضعیت آنلاین/آفلاین کاربر """
        self.user.is_online = is_online
        self.user.last_seen = now()
        self.user.save()
