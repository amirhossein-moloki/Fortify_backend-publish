from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta


class User(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="Phone Number")
    is_online = models.BooleanField(default=False, verbose_name="Online Status")
    last_seen = models.DateTimeField(blank=True, null=True, verbose_name="Last Seen")
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True,
                                        verbose_name="Profile Picture")
    bio = models.TextField(blank=True, null=True, verbose_name="Bio")

    # فیلدهای جدید برای OTP و تاریخ انقضا
    otp = models.CharField(max_length=6, blank=True, null=True, verbose_name="One Time Password (OTP)")
    otp_expiration = models.DateTimeField(blank=True, null=True, verbose_name="OTP Expiration Time")

    def __str__(self):
        return self.username

    def is_otp_valid(self):
        """ بررسی اعتبار کد OTP """
        if self.otp and self.otp_expiration:
            return timezone.now() < self.otp_expiration
        return False


class Profile(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", verbose_name="User")
    date_of_birth = models.DateField(blank=True, null=True, verbose_name="Date of Birth")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True, verbose_name="Gender")
    location = models.CharField(max_length=100, blank=True, null=True, verbose_name="Location")
    website = models.URLField(blank=True, null=True, verbose_name="Website")

    def __str__(self):
        return f"{self.user.username}'s Profile"
