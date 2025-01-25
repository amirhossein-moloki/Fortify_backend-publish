from django.core.management.base import BaseCommand
from accounts.models import User

class Command(BaseCommand):
    help = "Create a superuser if one does not already exist"

    def handle(self, *args, **kwargs):
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="amira",
                email="amir.moloki85@gmail.com",
                password="h@rad140252"
            )
            self.stdout.write("Admin user created successfully!")
        else:
            self.stdout.write("Admin user already exists!")
