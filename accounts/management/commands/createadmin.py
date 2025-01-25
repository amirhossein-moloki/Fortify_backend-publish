from django.core.management.base import BaseCommand
from accounts.models import User

class Command(BaseCommand):
    help = "Make the existing user 'amira' a superuser if they are not already."

    def handle(self, *args, **kwargs):
        try:
            user = User.objects.get(username="amira")
            if not user.is_superuser:
                user.is_superuser = True
                user.is_staff = True  # برای دسترسی به پنل مدیریت
                user.save()
                self.stdout.write("User 'amira' has been made a superuser!")
            else:
                self.stdout.write("User 'amira' is already a superuser.")
        except User.DoesNotExist:
            self.stdout.write("User 'amira' does not exist!")
