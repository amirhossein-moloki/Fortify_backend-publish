from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile

# سفارشی کردن نمایش مدل User در صفحه ادمین
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'profile_picture', 'bio')}),
        ('Status', {'fields': ('is_online', 'last_seen')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email'),
        }),
    )
    list_display = ('username', 'email', 'is_online', 'last_seen', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'phone_number')
    ordering = ('username',)

# مدیریت مدل Profile
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'date_of_birth', 'location', 'website')
    search_fields = ('user__username', 'location', 'gender')
    list_filter = ('gender', 'location')

# ثبت مدل‌ها در ادمین
admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
