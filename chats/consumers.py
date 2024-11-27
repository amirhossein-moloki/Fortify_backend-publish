import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message, Attachment
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.group_name = f"chat_{self.chat_id}"

        # ورود به گروه چت
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # خروج از گروه چت
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # دریافت پیام از WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'send':
            message_content = data.get('message')
            file = data.get('file')  # اطلاعات فایل

            sender = self.scope['user']

            # دریافت مشخصات فرستنده
            sender_name = sender.username
            sender_profile_picture = sender.profile_picture.url if sender.profile_picture else None
            sender_bio = sender.bio if sender.bio else ""

            # ذخیره پیام
            message = await self.save_message(sender, message_content)

            # در صورت وجود فایل، ذخیره فایل پیوست
            if file:
                attachment = await self.save_attachment(message, file)
                file_data = {
                    'file_name': attachment.file_name,
                    'file_type': attachment.file_type,
                    'file_size': attachment.file_size,
                }
            else:
                file_data = None

            # ارسال پیام به گروه چت
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'message': message.content,
                    'sender': sender_name,
                    'sender_profile_picture': sender_profile_picture,
                    'sender_bio': sender_bio,
                    'file': file_data,  # ارسال اطلاعات فایل
                    'action': 'send',  # علامت برای ارسال پیام
                    'message_id': message.id,
                }
            )

        elif action == 'edit':
            message_id = data.get('message_id')
            new_content = data.get('new_message')
            sender = self.scope['user']

            # ویرایش پیام
            message = await self.edit_message(message_id, new_content)

            # ارسال پیام ویرایش شده به گروه چت
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'message': message.content,
                    'sender': sender.username,
                    'sender_profile_picture': sender.profile_picture.url if sender.profile_picture else None,
                    'sender_bio': sender.bio if sender.bio else "",
                    'action': 'edit',  # علامت برای ویرایش پیام
                    'message_id': message.id,
                }
            )

        elif action == 'delete':
            message_id = data.get('message_id')
            sender = self.scope['user']

            # حذف پیام
            await self.delete_message(message_id)

            # ارسال پیام حذف شده به گروه چت
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'message_id': message_id,
                    'action': 'delete',  # علامت برای حذف پیام
                    'sender': sender.username,
                }
            )

        elif action == 'read':
            message_id = data.get('message_id')

            # علامت‌گذاری پیام به عنوان خوانده شده
            await self.mark_as_read(message_id)

            # ارسال اطلاع به گروه چت
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'message_id': message_id,
                    'action': 'read',  # علامت برای نشان دادن اینکه پیام خوانده شده است
                    'sender': self.scope['user'].username,
                }
            )

    # ذخیره پیام جدید
    @sync_to_async
    def save_message(self, sender, content):
        message = Message.objects.create(sender=sender, content=content, chat_id=self.chat_id)
        return message

    # ذخیره فایل پیوست
    @sync_to_async
    def save_attachment(self, message, file):
        attachment = Attachment.objects.create(
            message=message,
            file=file,
            file_name=file.name,
            file_type=file.content_type,
            file_size=file.size
        )
        return attachment

    # ویرایش پیام
    @sync_to_async
    def edit_message(self, message_id, new_content):
        message = Message.objects.get(id=message_id)
        message.content = new_content
        message.is_edited = True
        message.save()
        return message

    # حذف پیام
    @sync_to_async
    def delete_message(self, message_id):
        message = Message.objects.get(id=message_id)
        message.delete()  # حذف پیام از پایگاه داده

    # علامت‌گذاری پیام به عنوان خوانده شده
    @sync_to_async
    def mark_as_read(self, message_id):
        message = Message.objects.get(id=message_id)
        message.is_read = True
        message.read_by.add(self.scope['user'])  # کاربر را به لیست خوانندگان اضافه می‌کند
        message.save()

    # دریافت پیام از گروه چت
    async def chat_message(self, event):
        message = event.get('message')
        sender = event.get('sender')
        sender_profile_picture = event.get('sender_profile_picture')
        sender_bio = event.get('sender_bio')
        action = event.get('action')
        message_id = event.get('message_id')
        file = event.get('file')

        # ارسال پیام به WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'sender_profile_picture': sender_profile_picture,
            'sender_bio': sender_bio,
            'action': action,
            'message_id': message_id,
            'file': file,  # اطلاعات فایل پیوست
        }))
