from rest_framework import serializers
from .models import Notification, NotificationSettings

class NotificationSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'sender_name', 'notification_type', 'content', 'is_read', 'created_at', 'related_object_id', 'related_object_type']

    def get_sender_name(self, obj):
        return obj.sender.username if obj.sender else None

class NotificationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSettings
        fields = ['receive_messages', 'receive_friend_requests', 'receive_group_invites', 'receive_mentions']