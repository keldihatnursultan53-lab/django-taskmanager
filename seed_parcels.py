import os
from datetime import timedelta
from decimal import Decimal

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taskmanager.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone

from delivery.models import City, Parcel

User = get_user_model()
sender = User.objects.filter(username="sender1").first() or User.objects.first()
cities = {city.name: city for city in City.objects.all()}
now = timezone.now()

ROWS = [
    ("Aktau", "Almaty", "Laptop bag", "2.5", "M", 1, 6500),
    ("Aktau", "Almaty", "Documents", "0.3", "S", 2, 3000),
    ("Aktau", "Almaty", "Winter coat", "4", "L", 3, 8000),
    ("Aktau", "Astana", "Gift box", "1.2", "S", 2, 5000),
    ("Aktau", "Astana", "Books set", "6", "L", 4, 9500),
    ("Aktau", "Shymkent", "Phone case", "0.2", "S", 1, 2500),
    ("Aktau", "Shymkent", "Shoes", "1.8", "M", 2, 5500),
    ("Aktau", "Aktobe", "Spare parts", "7", "L", 3, 9000),
    ("Aktau", "Aktobe", "Tea set", "3", "M", 5, 6000),
    ("Almaty", "Aktau", "Medicine papers", "0.4", "S", 1, 3500),
    ("Almaty", "Aktau", "Camera", "2", "M", 2, 7000),
    ("Almaty", "Astana", "Gift bag", "1.5", "S", 3, 4500),
    ("Astana", "Aktau", "Souvenirs", "2.2", "M", 2, 6000),
    ("Astana", "Almaty", "Box of cables", "5", "L", 4, 8500),
    ("Shymkent", "Aktau", "Dried fruits", "3.5", "M", 1, 6500),
    ("Shymkent", "Almaty", "Small parcel", "0.8", "S", 2, 3000),
    ("Aktobe", "Aktau", "Tools", "8", "L", 3, 10000),
    ("Aktobe", "Astana", "Documents pack", "0.5", "S", 1, 3200),
    ("Aktau", "Almaty", "Toys", "3", "M", 6, 6200),
    ("Aktau", "Astana", "Blanket", "4.5", "L", 5, 8800),
]

created = 0
for from_name, to_name, title, weight, size, days, price in ROWS:
    _, was_created = Parcel.objects.get_or_create(
        sender=sender,
        title=title,
        defaults={
            "from_city": cities[from_name],
            "to_city": cities[to_name],
            "declared_contents": "Test item, no restricted goods",
            "weight_kg": Decimal(weight),
            "size": size,
            "pickup_from": now + timedelta(days=days),
            "deliver_by": now + timedelta(days=days + 3),
            "price": Decimal(price),
            "is_declaration_confirmed": True,
        },
    )
    created += was_created

print(f"Created: {created}. Total parcels: {Parcel.objects.count()}")
