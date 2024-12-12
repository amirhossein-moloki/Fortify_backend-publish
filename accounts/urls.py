from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterAPIView.as_view(), name='register'),
    path('login/', views.LoginAPIView.as_view(), name='login'),
    path('logout/', views.LogoutAPIView.as_view(), name='logout'),
    path('activate-email/<str:uidb64>/<str:token>/', views.ActivateEmailAPIView.as_view(), name='activate_email'),
    path('password-reset/', views.PasswordResetAPIView.as_view(), name='password_reset'),
    path('password-reset-confirm/<str:uidb64>/<str:token>/', views.PasswordResetConfirmAPIView.as_view(), name='password_reset_confirm'),
    path('password-change/<str:uidb64>/<str:token>/', views.PasswordChangeAPIView.as_view(), name='password_change'),
    path('profile/update/', views.UpdateProfileAPIView.as_view(), name='update_profile'),
    path('profile/<int:user_id>/', views.UserProfileView.as_view(), name='user_profile'),
    path('search/', views.SearchUserView.as_view(), name='search_user'),
    path('delete-account/', views.DeleteAccountAPIView.as_view(), name='delete_account'),
    path('login-verify/<str:otp>/', views.OTPVerifyAPIView.as_view(), name='otp_verify'),
]