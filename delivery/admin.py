from django.contrib import admin

from .models import City, Delivery, LocationPing, Offer, Parcel, Payment, Profile, Trip


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "region")
    search_fields = ("name",)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "home_city", "is_verified")


@admin.register(Parcel)
class ParcelAdmin(admin.ModelAdmin):
    list_display = ("title", "sender", "from_city", "to_city", "price", "status", "created_at")
    list_filter = ("status", "from_city", "to_city")
    search_fields = ("title", "declared_contents")


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ("courier", "from_city", "to_city", "departure_at", "status")
    list_filter = ("status", "transport")


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ("parcel", "courier", "price", "status")
    list_filter = ("status",)


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ("parcel", "courier", "total_price", "status")
    list_filter = ("status",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("delivery", "payer", "amount", "status")
    list_filter = ("status",)


@admin.register(LocationPing)
class LocationPingAdmin(admin.ModelAdmin):
    list_display = ("delivery", "latitude", "longitude", "recorded_at")