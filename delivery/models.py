from decimal import Decimal

from django.conf import settings
from django.db import models


class City(models.Model):
    name = models.CharField(max_length=100, unique=True)
    region = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name_plural = "cities"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=20, blank=True)
    home_city = models.ForeignKey(City, null=True, blank=True, on_delete=models.SET_NULL, related_name="residents")
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile of {self.user.username}"


class Parcel(models.Model):
    class Size(models.TextChoices):
        S = "S", "Small"
        M = "M", "Medium"
        L = "L", "Large"

    class HandoverMethod(models.TextChoices):
        COURIER_PICKUP = "courier_pickup", "Courier picks up"
        SENDER_DROPOFF = "sender_dropoff", "Sender drops off"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        ASSIGNED = "assigned", "Assigned"
        IN_TRANSIT = "in_transit", "In transit"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="parcels")
    from_city = models.ForeignKey(City, on_delete=models.PROTECT, related_name="outgoing_parcels")
    to_city = models.ForeignKey(City, on_delete=models.PROTECT, related_name="incoming_parcels")
    title = models.CharField(max_length=200)
    declared_contents = models.TextField()
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2)
    size = models.CharField(max_length=1, choices=Size.choices, default=Size.S)
    pickup_from = models.DateTimeField()
    deliver_by = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    allow_offers = models.BooleanField(default=True)
    handover_method = models.CharField(max_length=20, choices=HandoverMethod.choices, default=HandoverMethod.SENDER_DROPOFF)
    pickup_address = models.CharField(max_length=255, blank=True)
    pickup_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    is_declaration_confirmed = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="received_parcels")
    recipient_phone = models.CharField(max_length=20, blank=True)
    confirmation_code = models.CharField(max_length=6, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title}: {self.from_city} -> {self.to_city}"


class Trip(models.Model):
    class Transport(models.TextChoices):
        CAR = "car", "Car"
        BUS = "bus", "Bus"
        TRAIN = "train", "Train"
        PLANE = "plane", "Plane"

    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    courier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="trips")
    from_city = models.ForeignKey(City, on_delete=models.PROTECT, related_name="departing_trips")
    to_city = models.ForeignKey(City, on_delete=models.PROTECT, related_name="arriving_trips")
    departure_at = models.DateTimeField()
    free_capacity_kg = models.DecimalField(max_digits=6, decimal_places=2)
    transport = models.CharField(max_length=10, choices=Transport.choices, default=Transport.CAR)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PLANNED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["departure_at"]

    def __str__(self):
        return f"{self.from_city} -> {self.to_city} ({self.departure_at:%d.%m.%Y})"


class Offer(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"
        WITHDRAWN = "withdrawn", "Withdrawn"

    parcel = models.ForeignKey(Parcel, on_delete=models.CASCADE, related_name="offers")
    courier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="offers")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["parcel", "courier"],
                condition=models.Q(status="pending"),
                name="unique_pending_offer_per_courier",
            )
        ]

    def __str__(self):
        return f"Offer {self.price} for {self.parcel}"


class Delivery(models.Model):
    class Status(models.TextChoices):
        ACCEPTED = "accepted", "Accepted"
        PICKED_UP = "picked_up", "Picked up"
        DELIVERED = "delivered", "Delivered"
        CONFIRMED = "confirmed", "Confirmed by recipient"
        REFUSED = "refused", "Refused"

    parcel = models.OneToOneField(Parcel, on_delete=models.CASCADE, related_name="delivery")
    courier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="deliveries")
    trip = models.ForeignKey(Trip, null=True, blank=True, on_delete=models.SET_NULL, related_name="deliveries")
    offer = models.ForeignKey(Offer, null=True, blank=True, on_delete=models.SET_NULL, related_name="deliveries")
    agreed_price = models.DecimalField(max_digits=10, decimal_places=2)
    pickup_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    accepted_at = models.DateTimeField(auto_now_add=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACCEPTED)
    comment = models.TextField(blank=True)

    def __str__(self):
        return f"Delivery of {self.parcel}"


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        HELD = "held", "Held by platform"
        RELEASED = "released", "Released to courier"
        REFUNDED = "refunded", "Refunded"
        DISPUTED = "disputed", "Disputed"

    delivery = models.OneToOneField(Delivery, on_delete=models.CASCADE, related_name="payment")
    payer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    held_at = models.DateTimeField(null=True, blank=True)
    released_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.amount} ({self.status})"


class LocationPing(models.Model):
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name="pings")
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recorded_at"]

    def __str__(self):
        return f"{self.latitude}, {self.longitude}"

class TripStop(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="stops")
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name="trip_stops")
    order = models.PositiveSmallIntegerField()
    arrival_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(fields=["trip", "order"], name="unique_stop_order_per_trip"),
        ]

    def __str__(self):
        return f"Trip {self.trip_id}: {self.order}. {self.city}"