from rest_framework import serializers
from .models import Chat, Message, Attachment, Role
from accounts.models import User

# سریالایزر برای User
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email','profile_picture')  # می‌توانید فیلدهای مورد نیاز خود را اضافه کنید

# سریالایزر برای مدل Chat
class ChatSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True)  # نمایش شرکت‌کنندگان
    group_admin = UserSerializer()  # نمایش ادمین گروه
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Chat
        fields = ('id', 'participants', 'created_at', 'updated_at', 'chat_type', 'group_name', 'group_admin','group_image','max_participants', 'description')

# سریالایزر برای مدل Message
class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer()  # نمایش فرستنده پیام
    chat = ChatSerializer()  # نمایش چت مربوطه
    timestamp = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    read_by = UserSerializer(many=True)  # نمایش کاربرانی که پیام را خوانده‌اند

    class Meta:
        model = Message
        fields = ('id', 'chat', 'sender', 'content', 'timestamp', 'is_read', 'read_by', 'is_edited', 'is_deleted')

# سریالایزر برای مدل Attachment
class AttachmentSerializer(serializers.ModelSerializer):
    message = MessageSerializer()  # نمایش پیام مربوطه

    class Meta:
        model = Attachment
        fields = ('id', 'message', 'file', 'file_name', 'file_type', 'file_size')

# سریالایزر برای مدل Role
class RoleSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # نمایش کاربر
    chat = ChatSerializer()  # نمایش چت مربوطه

    class Meta:
        model = Role
        fields = ('id', 'user', 'chat', 'role')

from .models import Chat, Message
from accounts.models import User
from rest_framework import serializers

class GetChatsSerializer(serializers.ModelSerializer):
    # شمارش پیام‌های خوانده نشده برای کاربر
    unread_count = serializers.SerializerMethodField()

    # اطلاعات کاربر دیگر در چت‌های مستقیم
    other_user = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ['id', 'chat_type', 'name', 'image', 'unread_count', 'other_user']

    def get_unread_count(self, obj):
        user = self.context['request'].user
        return obj.unread_message_count(user)

    def get_other_user(self, obj):
        user = self.context['request'].user
        if obj.chat_type == 'direct':
            other_user = obj.participants.exclude(id=user.id).first()
            if other_user:
                return UserSerializer(other_user).data
        return None

    def get_name(self, obj):
        # برای چت‌های مستقیم، نام کاربر دیگر را می‌گیریم
        if obj.chat_type == 'direct':
            other_user = obj.participants.exclude(id=self.context['request'].user.id).first()
            return other_user.username if other_user else "Unknown User"
        return obj.group_name if obj.group_name else f"Chat {obj.id}"

    def get_image(self, obj):
        if obj.chat_type == 'direct':
            other_user = obj.participants.exclude(id=self.context['request'].user.id).first()
            return other_user.profile_picture.url if other_user and other_user.profile_picture else None
        return obj.group_image.url if obj.group_image else None
