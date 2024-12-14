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
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.group_name = f"chat_{self.chat_id}"

        token = self.get_token_from_query_string(self.scope)

        if not token:
            for header in self.scope.get('headers', []):
                if header[0] == b'authorization':
                    token = header[1].decode().split(' ')[1]
                    break

        if not token:
            await self.close()
            return

        try:
            user = await self.get_user_from_token(token)

            if user is None:
                raise AuthenticationFailed("Invalid token")

            self.scope['user'] = user

            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()

            messages = await self.get_messages()

            for message in messages:
                sender_name = await self.get_sender_username(message)
                sender_profile_picture = await self.get_sender_profile_picture(message)
                sender_bio = await self.get_sender_bio(message)

                await self.send(text_data=json.dumps({
                    'message': message.content,
                    'sender': sender_name,
                    'sender_profile_picture': sender_profile_picture,
                    'sender_bio': sender_bio,
                    'timestamp': message.timestamp.isoformat(),
                    'read_by': [user.username for user in await database_sync_to_async(list)(message.read_by.all())],
                    'is_edited': message.is_edited,
                    'is_deleted': message.is_deleted,
                    'action': 'send',
                    'message_id': message.id,
                    'file': None,
                }))

        except AuthenticationFailed:
            await self.close()

    def get_token_from_query_string(self, scope):
        token = parse_qs(scope.get('query_string', b'').decode()).get('token', [None])[0]
        return token

    # بخش مربوط به دریافت داده‌ها از WebSocket و ارسال رویدادها به گروه
    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'send':
            message_content = data.get('message')
            file = data.get('file')
            sender = self.scope['user']

            message = await self.save_message(sender, message_content)

            sender_name = sender.username
            sender_profile_picture = sender.profile_picture.url if sender.profile_picture else None
            sender_bio = sender.bio if sender.bio else ""

            if file:
                attachment = await self.save_attachment(message, file)
                file_data = {
                    'file_name': attachment.file_name,
                    'file_type': attachment.file_type,
                    'file_size': attachment.file_size,
                }
            else:
                file_data = None

            # ارسال پیام به گروه به روز شده
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'message': message.content,
                    'sender': sender_name,
                    'sender_profile_picture': sender_profile_picture,
                    'sender_bio': sender_bio,
                    'timestamp': message.timestamp.isoformat(),
                    'read_by': [user.username for user in await database_sync_to_async(list)(message.read_by.all())],
                    'is_edited': message.is_edited,
                    'is_deleted': message.is_deleted,
                    'action': 'send',
                    'message_id': message.id,
                    'file': file_data,
                }
            )

        elif action == 'edit':
            message_id = data.get('message_id')
            new_content = data.get('new_message')
            sender = self.scope['user']

            # ویرایش پیام
            message = await self.edit_message(message_id, new_content)

            # ارسال پیام ویرایش شده به گروه
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'message': message.content,
                    'sender': sender.username,
                    'sender_profile_picture': sender.profile_picture.url if sender.profile_picture else None,
                    'sender_bio': sender.bio if sender.bio else "",
                    'timestamp': message.timestamp.isoformat(),
                    'read_by': [user.username for user in await database_sync_to_async(list)(message.read_by.all())],
                    'is_edited': message.is_edited,
                    'is_deleted': message.is_deleted,
                    'action': 'edit',
                    'message_id': message.id,
                }
            )

        elif action == 'delete':
            message_id = data.get('message_id')
            sender = self.scope['user']

            # حذف پیام
            await self.delete_message(message_id)

            # ارسال پیام حذف شده به گروه
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

            # ارسال اطلاعات خوانده شده به گروه
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'message_id': message_id,
                    'action': 'read',
                    'read_by': [user.username for user in
                                await database_sync_to_async(list)((await self.get_message_read_by(message_id)))],
                    'sender': self.scope['user'].username,
                }
            )

    # مدیریت دریافت پیام‌ها در گروه (نمایش پیام‌ها)
    async def chat_message(self, event):
        message = event.get('message')
        if not message:
            return

        sender_name = event.get('sender')
        sender_profile_picture = event.get('sender_profile_picture')
        sender_bio = event.get('sender_bio')
        timestamp = event.get('timestamp')
        read_by = event.get('read_by')
        is_edited = event.get('is_edited')
        is_deleted = event.get('is_deleted')
        action = event.get('action')
        message_id = event.get('message_id')
        file_data = event.get('file')

        # ارسال داده‌ها به WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'sender': sender_name,
            'sender_profile_picture': sender_profile_picture,
            'sender_bio': sender_bio,
            'timestamp': timestamp,
            'read_by': read_by,
            'is_edited': is_edited,
            'is_deleted': is_deleted,
            'action': action,
            'message_id': message_id,
            'file': file_data,
        }))

    @database_sync_to_async
    def save_message(self, sender, content):
        message = Message.objects.create(sender=sender, content=content, chat_id=self.chat_id)
        message.is_read = True
        message.read_by.add(sender)
        message.save()
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
        if self.scope['user'] not in message.read_by.all():
            message.is_read = True
            message.read_by.add(self.scope['user'])
            message.save()

    @database_sync_to_async
    def get_messages(self):
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

    @database_sync_to_async
    def get_message_read_by(self, message_id):
        message = Message.objects.get(id=message_id)
        return message.read_by.all()

    async def chat_message(self, event):
        message = event.get('message')
        if not message:
            return

        sender_name = event.get('sender')
        sender_profile_picture = event.get('sender_profile_picture')
        sender_bio = event.get('sender_bio')
        timestamp = event.get('timestamp')
        read_by = event.get('read_by')
        is_edited = event.get('is_edited')
        is_deleted = event.get('is_deleted')
        action = event.get('action')
        message_id = event.get('message_id')
        file_data = event.get('file')

        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'sender': sender_name,
            'sender_profile_picture': sender_profile_picture,
            'sender_bio': sender_bio,
            'timestamp': timestamp,
            'read_by': read_by,
            'is_edited': is_edited,
            'is_deleted': is_deleted,
            'action': action,
            'message_id': message_id,
            'file': file_data,
        }))
