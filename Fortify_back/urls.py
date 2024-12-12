from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),  # URLهای مربوط به حساب‌ها
    path('api/chats/', include('chats.urls')),  # URLهای مربوط به چت‌ها (برای درخواست‌های API)
]

# افزودن تنظیمات برای فایل‌های مدیا
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
