from rest_framework import serializers
from .models import User, Profile
from django.core.exceptions import ValidationError

from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_online', 'last_seen', 'profile_picture', 'bio']

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def to_representation(self, instance):
        """
        برای نمایش بهتر اطلاعات، در صورت نیاز، اطلاعات خاصی را برای هر فرد
        به‌ویژه فیلدهای `username` و `profile_picture` می‌توان به‌طور ویژه برگشت داد.
        """
        representation = super().to_representation(instance)
        representation['username'] = instance.username
        representation['profile_picture'] = instance.profile_picture.url if instance.profile_picture else None
        return representation

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # نمایش اطلاعات مربوط به کاربر

    class Meta:
        model = Profile
        fields = ['id', 'user', 'date_of_birth', 'gender', 'location', 'website']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']

    def validate_username(self, value):
        """Check if the username already exists"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_email(self, value):
        """Check if the email already exists"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already taken.")
        return value

    def validate(self, data):
        """Check if the password and confirm password match"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return data

    def create(self, validated_data):
        """Create a new user and hash the password"""
        password = validated_data.pop('password')
        validated_data.pop('password_confirm', None)  # Remove password_confirm field

        user = User(**validated_data)
        user.set_password(password)  # Hash the password before saving
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)
