import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Automatically creates or updates an admin superuser account for the dashboard."

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "adminpassword123")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@qurontutor.uz")

        user, created = User.objects.get_or_create(username=username, defaults={"email": email})
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created successfully!"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' password updated successfully!"))