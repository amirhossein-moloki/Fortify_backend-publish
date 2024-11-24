from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.models import User
from django.http import Http404
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import UserSerializer, ProfileSerializer
from django.contrib.auth.forms import PasswordResetForm
from django_ratelimit.decorators import ratelimit  # اضافه کردن دکوریتور

# ویو ثبت‌نام کاربر
class RegisterAPIView(APIView):
    @ratelimit(key='ip', rate='5/m', method='ALL', burst=True)  # محدود کردن به 5 درخواست در دقیقه
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # ایجاد توکن JWT
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # ارسال ایمیل تایید (اختیاری) با قالب HTML
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(str(user.pk).encode())
            verification_link = f'http://yourdomain.com/activate-email/{uid}/{token}/'

            email_subject = 'Email Confirmation'
            email_message = f'<p>Click the link to confirm your email: <a href="{verification_link}">Confirm Email</a></p>'
            send_mail(
                email_subject,
                email_message,
                'admin@example.com',
                [user.email],
                fail_silently=False,
                html_message=email_message  # ارسال ایمیل با قالب HTML
            )

            return Response({
                "message": "Please confirm your email address to complete the registration.",
                "access_token": access_token
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ویو ورود کاربر (Login) با JWT
class LoginAPIView(APIView):
    @ratelimit(key='ip', rate='5/m', method='ALL', burst=True)  # محدود کردن به 5 درخواست در دقیقه
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                return Response({
                    "message": "Login successful!",
                    "access_token": access_token
                }, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Account not activated."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)


# ویو تایید ایمیل
class ActivateEmailAPIView(APIView):
    @ratelimit(key='ip', rate='5/m', method='ALL', burst=True)  # محدود کردن به 5 درخواست در دقیقه
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))  # تبدیل رشته به force_str
            user = User.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                user.is_active = True
                user.save()
                return Response({"message": "Email successfully confirmed!"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"message": "Invalid token or user does not exist."}, status=status.HTTP_400_BAD_REQUEST)


# ویو برای بازیابی رمز عبور
class PasswordResetAPIView(APIView):
    @ratelimit(key='ip', rate='5/m', method='ALL', burst=True)  # محدود کردن به 5 درخواست در دقیقه
    def post(self, request):
        email = request.data.get('email')
        form = PasswordResetForm(data={'email': email})

        if form.is_valid():
            user = form.get_users(email)[0]
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(str(user.pk).encode())
            reset_link = f'http://yourdomain.com/reset-password/{uid}/{token}/'

            # ارسال ایمیل با قالب HTML
            email_subject = 'Password Reset'
            email_message = f'<p>Click the link to reset your password: <a href="{reset_link}">Reset Password</a></p>'
            send_mail(
                email_subject,
                email_message,
                'admin@example.com',
                [user.email],
                fail_silently=False,
                html_message=email_message  # ایمیل با قالب HTML
            )

            return Response({"message": "Password reset email sent."}, status=status.HTTP_200_OK)
        return Response({"message": "Invalid email address."}, status=status.HTTP_400_BAD_REQUEST)


# ویو تایید بازیابی رمز عبور
class PasswordResetConfirmAPIView(APIView):
    @ratelimit(key='ip', rate='5/m', method='ALL', burst=True)  # محدود کردن به 5 درخواست در دقیقه
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))  # تبدیل رشته به force_str
            user = User.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                return Response({"message": "Token is valid. You can reset your password."}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"message": "Invalid token or user does not exist."}, status=status.HTTP_400_BAD_REQUEST)


# ویو برای تغییر رمز عبور
class PasswordChangeAPIView(APIView):
    @ratelimit(key='ip', rate='5/m', method='ALL', burst=True)  # محدود کردن به 5 درخواست در دقیقه
    def post(self, request, uidb64, token):
        password = request.data.get('password')
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))  # تبدیل رشته به force_str
            user = User.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                user.set_password(password)
                user.save()
                return Response({"message": "Password changed successfully!"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"message": "Invalid token or user does not exist."}, status=status.HTTP_400_BAD_REQUEST)


# ویو برای آپدیت پروفایل کاربری با JWT
class UpdateProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    @ratelimit(key='ip', rate='5/m', method='ALL', burst=True)  # محدود کردن به 5 درخواست در دقیقه
    def put(self, request):
        user = request.user
        profile_data = request.data.get('profile', {})

        # بررسی وجود پروفایل کاربر
        if not hasattr(user, 'profile'):
            return Response({"message": "Profile does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # آپدیت پروفایل
        profile_serializer = ProfileSerializer(user.profile, data=profile_data, partial=True)

        if profile_serializer.is_valid():
            profile_serializer.save()
            return Response({"message": "Profile updated successfully!"}, status=status.HTTP_200_OK)
        return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ویو برای خروج کاربر
class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]
    @ratelimit(key='ip', rate='5/m', method='ALL', burst=True)  # محدود کردن به 5 درخواست در دقیقه
    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()  # غیرفعال کردن توکن
            return Response({"message": "Logout successful!"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


# ویو برای حذف حساب کاربری
class DeleteAccountAPIView(APIView):
    permission_classes = [IsAuthenticated]
    @ratelimit(key='ip', rate='5/m', method='ALL', burst=True)  # محدود کردن به 5 درخواست در دقیقه
    def delete(self, request):
        user = request.user
        user.delete()
        return Response({"message": "Account deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
