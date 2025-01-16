import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils.timezone import now


class AccountStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_authenticated:
            self.user = self.scope["user"]
            # به‌روزرسانی وضعیت آنلاین
            await self.update_user_status(is_online=True)
            await self.accept()
        else:
            # رد کردن اتصال در صورتی که کاربر احراز هویت نشده باشد
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'user'):
            # به‌روزرسانی وضعیت آفلاین
            await self.update_user_status(is_online=False)

    async def receive(self, text_data):
        """
        دریافت داده‌های ورودی از کلاینت و پردازش آن.
        اینجا می‌توانید پیام‌های خاصی را از کلاینت مدیریت کنید.
        """
        data = json.loads(text_data)
        message = data.get("message", "No message received.")

        # ارسال پاسخ به کلاینت
        await self.send(text_data=json.dumps({
            "message": f"Received: {message}"
        }))

    @database_sync_to_async
    def update_user_status(self, is_online):
        """ به‌روزرسانی وضعیت آنلاین/آفلاین کاربر """
        self.user.is_online = is_online
        self.user.last_seen = now()
        self.user.save()
