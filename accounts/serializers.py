from rest_framework import serializers
from .models import User, Profile
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'is_online', 'last_seen', 'profile_picture', 'bio']

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # نمایش اطلاعات مربوط به کاربر

    class Meta:
        model = Profile
        fields = ['id', 'user', 'date_of_birth', 'gender', 'location', 'website']



from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password', 'password_confirm']

    def validate_username(self, value):
        """ چک می‌کنیم که یوزرنیم تکراری نباشد """
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_email(self, value):
        """ چک می‌کنیم که ایمیل تکراری نباشد """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already taken.")
        return value

    def validate(self, data):
        """ چک می‌کنیم که رمز عبور و تایید آن یکی باشند """
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return data

    def create(self, validated_data):
        """ کاربر جدید را ایجاد می‌کنیم """
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # رمز عبور را هش می‌کنیم
        user.save()
        return user


from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)
