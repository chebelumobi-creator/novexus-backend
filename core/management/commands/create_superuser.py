from django.core.management.base import BaseCommand
from core.models import User

class Command(BaseCommand):
    help = "Create a superuser if none exists"

    def handle(self, *args, **options):
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@email.com", "admin123")
            self.stdout.write(self.style.SUCCESS("✅ Superuser created!"))
        else:
            self.stdout.write("ℹ️ Superuser already exists.")
