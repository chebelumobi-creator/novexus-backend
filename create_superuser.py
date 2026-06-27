import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "remedybank.settings")
django.setup()

from core.models import User

email = "admin@email.com"
username = "admin"
password = "admin123"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"Superuser \"{username}\" created successfully!")
else:
    print(f"Superuser \"{username}\" already exists.")
