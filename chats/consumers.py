import json
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message, Attachment, Chat
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # دریافت شناسه چت از URL
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.group_name = f"chat_{self.chat_id}"

        # تلاش برای استخراج توکن از query string
        token = self.get_token_from_query_string(self.scope)

        # اگر توکن از query string پیدا نشد، تلاش برای دریافت توکن از هدر Authorization
        if not token:
            for header in self.scope.get('headers', []):
                if header[0] == b'authorization':
                    token = header[1].decode().split(' ')[1]  # Bearer <token>
                    break

        # اگر هیچ توکنی پیدا نشد، اتصال را می‌بندیم
        if not token:
            await self.close()
            return

        try:
            # اعتبارسنجی توکن و استخراج کاربر
            user = await self.get_user_from_token(token)

            if user is None:
                raise AuthenticationFailed("Invalid token")

            # اضافه کردن کاربر به scope
            self.scope['user'] = user

            # ورود به گروه چت
            await self.channel_layer.group_add(self.group_name, self.channel_name)

            # تایید اتصال قبل از ارسال پیام‌ها
            await self.accept()

            # ارسال پیام‌های موجود در چت به کاربر
            messages = await self.get_messages()

            for message in messages:
                sender_name = await self.get_sender_username(message)
                sender_profile_picture = await self.get_sender_profile_picture(message)
                sender_bio = await self.get_sender_bio(message)

                action = 'send'

                await self.send(text_data=json.dumps({
                    'message': message.content,
                    'sender': sender_name,
                    'sender_profile_picture': sender_profile_picture,
                    'sender_bio': sender_bio,
                    'action': action,
                    'message_id': message.id,
                    'file': None,  # فرض می‌کنیم این پیام‌ها فایل ندارند
                }))

        except AuthenticationFailed:
            await self.close()

    def get_token_from_query_string(self, scope):
        """استخراج توکن از query string"""
        token = parse_qs(scope.get('query_string', b'').decode()).get('token', [None])[0]
        return token

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'send':
            message_content = data.get('message')
            file = data.get('file')

            sender = self.scope['user']

            sender_name = sender.username
            sender_profile_picture = sender.profile_picture.url if sender.profile_picture else None
            sender_bio = sender.bio if sender.bio else ""

            message = await self.save_message(sender, message_content)

            if file:
                attachment = await self.save_attachment(message, file)
                file_data = {
                    'file_name': attachment.file_name,
                    'file_type': attachment.file_type,
                    'file_size': attachment.file_size,
                }
            else:
                file_data = None

            # ارسال پیام به گروه
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'message': message.content,
                    'sender': sender_name,
                    'sender_profile_picture': sender_profile_picture,
                    'sender_bio': sender_bio,
                    'file': file_data,
                    'action': 'send',
                    'message_id': message.id,
                }
            )

        elif action == 'edit':
            message_id = data.get('message_id')
            new_content = data.get('new_message')
            sender = self.scope['user']

            message = await self.edit_message(message_id, new_content)

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'message': message.content,
                    'sender': sender.username,
                    'sender_profile_picture': sender.profile_picture.url if sender.profile_picture else None,
                    'sender_bio': sender.bio if sender.bio else "",
                    'action': 'edit',
                    'message_id': message.id,
                }
            )

        elif action == 'delete':
            message_id = data.get('message_id')
            sender = self.scope['user']

            await self.delete_message(message_id)

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'message_id': message_id,
                    'action': 'delete',
                    'sender': sender.username,
                }
            )

        elif action == 'read':
            message_id = data.get('message_id')

            await self.mark_as_read(message_id)

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'message_id': message_id,
                    'action': 'read',
                    'sender': self.scope['user'].username,
                }
            )

    @database_sync_to_async
    def save_message(self, sender, content):
        message = Message.objects.create(sender=sender, content=content, chat_id=self.chat_id)
        return message

    @database_sync_to_async
    def save_attachment(self, message, file):
        attachment = Attachment.objects.create(
            message=message,
            file=file,
            file_name=file.name,
            file_type=file.content_type,
            file_size=file.size
        )
        return attachment

    @database_sync_to_async
    def edit_message(self, message_id, new_content):
        message = Message.objects.get(id=message_id)
        message.content = new_content
        message.is_edited = True
        message.save()
        return message

    @database_sync_to_async
    def delete_message(self, message_id):
        message = Message.objects.get(id=message_id)
        message.delete()

    @database_sync_to_async
    def mark_as_read(self, message_id):
        message = Message.objects.get(id=message_id)
        message.is_read = True
        message.read_by.add(self.scope['user'])
        message.save()

    @database_sync_to_async
    def get_messages(self):
        # عملیات پایگاه داده که باید به صورت همزمان انجام شود
        return list(Message.objects.filter(chat=self.chat_id).order_by('timestamp'))

    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = get_user_model().objects.get(id=user_id)
            return user
        except (Exception, AuthenticationFailed):
            return None

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        sender_profile_picture = event['sender_profile_picture']
        sender_bio = event['sender_bio']
        action = event['action']
        message_id = event['message_id']
        file_data = event.get('file')

        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'sender_profile_picture': sender_profile_picture,
            'sender_bio': sender_bio,
            'action': action,
            'message_id': message_id,
            'file': file_data,
        }))

    @database_sync_to_async
    def get_sender_username(self, message):
        return message.sender.username

    @database_sync_to_async
    def get_sender_profile_picture(self, message):
        return message.sender.profile_picture.url if message.sender.profile_picture else None

    @database_sync_to_async
    def get_sender_bio(self, message):
        return message.sender.bio if message.sender.bio else ""
