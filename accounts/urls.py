from django.urls import path
from .views import (
    RegisterAPIView,
    LoginAPIView,
    ActivateEmailAPIView,
    PasswordResetAPIView,
    PasswordResetConfirmAPIView,
    PasswordChangeAPIView,
    UpdateProfileAPIView,
    LogoutAPIView,
    DeleteAccountAPIView,
    OTPVerifyAPIView
)

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),  # ثبت‌نام کاربر
    path('login/', LoginAPIView.as_view(), name='login'),  # ورود کاربر
    path('login-verify/<str:otp>/', OTPVerifyAPIView.as_view(), name='otp-verify'),
    path('activate-email/<str:uidb64>/<str:token>/', ActivateEmailAPIView.as_view(), name='activate-email'),  # تایید ایمیل
    path('password-reset/', PasswordResetAPIView.as_view(), name='password-reset'),  # درخواست بازیابی رمز عبور
    path('reset-password/<str:uidb64>/<str:token>/', PasswordResetConfirmAPIView.as_view(), name='password-reset-confirm'),  # تایید بازیابی رمز عبور
    path('password-change/<str:uidb64>/<str:token>/', PasswordChangeAPIView.as_view(), name='password-change'),  # تغییر رمز عبور
    path('update-profile/', UpdateProfileAPIView.as_view(), name='update-profile'),  # آپدیت پروفایل کاربری
    path('logout/', LogoutAPIView.as_view(), name='logout'),  # خروج کاربر
    path('delete-account/', DeleteAccountAPIView.as_view(), name='delete-account'),  # حذف حساب کاربری
]
