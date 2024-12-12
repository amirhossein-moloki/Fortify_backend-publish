from django.contrib import admin
from .models import Chat, Message, Attachment, Role

# تنظیمات مدل Chat
@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat_type', 'group_name', 'group_admin', 'created_at', 'updated_at')
    list_filter = ('chat_type', 'created_at')
    search_fields = ('group_name', 'group_admin__username')
    filter_horizontal = ('participants',)  # برای مدیریت راحت‌تر شرکت‌کنندگان
    readonly_fields = ('created_at', 'updated_at')  # جلوگیری از ویرایش این فیلدها

# تنظیمات مدل Message
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'sender', 'content', 'timestamp', 'is_read', 'is_edited', 'is_deleted')
    list_filter = ('is_read', 'is_edited', 'is_deleted', 'timestamp')
    search_fields = ('content', 'sender__username', 'chat__group_name')
    autocomplete_fields = ('chat', 'sender')  # برای انتخاب سریع‌تر چت و فرستنده

# تنظیمات مدل Attachment
@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'file_name', 'file_type', 'file_size')
    search_fields = ('file_name', 'message__content')

# تنظیمات مدل Role
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'chat', 'role')
    list_filter = ('role',)
    search_fields = ('user__username', 'chat__group_name')
