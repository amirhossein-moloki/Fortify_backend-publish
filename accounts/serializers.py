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
