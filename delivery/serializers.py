from rest_framework import serializers

from .models import City, Parcel, Trip, TripStop


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ["id", "name", "region"]


class ParcelSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source="sender.username", read_only=True)
    from_city_name = serializers.CharField(source="from_city.name", read_only=True)
    to_city_name = serializers.CharField(source="to_city.name", read_only=True)

    class Meta:
        model = Parcel
        fields = [
            "id",
            "sender",
            "sender_username",
            "from_city",
            "from_city_name",
            "to_city",
            "to_city_name",
            "title",
            "declared_contents",
            "weight_kg",
            "size",
            "pickup_from",
            "deliver_by",
            "price",
            "allow_offers",
            "handover_method",
            "pickup_address",
            "pickup_fee",
            "is_declaration_confirmed",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "status", "created_at"]
        extra_kwargs = {
            "is_declaration_confirmed": {"required": True},
        }

    def validate_weight_kg(self, value):
        if value <= 0:
            raise serializers.ValidationError("Weight must be greater than zero.")
        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value


class TripStopSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source="city.name", read_only=True)

    class Meta:
        model = TripStop
        fields = ["id", "trip", "city", "city_name", "order", "arrival_at"]
        read_only_fields = ["id", "trip"]

    def validate_order(self, value):
        if value < 1:
            raise serializers.ValidationError("Order must be 1 or greater.")
        return value


class TripSerializer(serializers.ModelSerializer):
    courier_username = serializers.CharField(source="courier.username", read_only=True)
    from_city_name = serializers.CharField(source="from_city.name", read_only=True)
    to_city_name = serializers.CharField(source="to_city.name", read_only=True)
    stops = TripStopSerializer(many=True, read_only=True)

    class Meta:
        model = Trip
        fields = [
            "id",
            "courier",
            "courier_username",
            "from_city",
            "from_city_name",
            "to_city",
            "to_city_name",
            "departure_at",
            "free_capacity_kg",
            "transport",
            "status",
            "created_at",
            "stops",
        ]
        read_only_fields = ["id", "status", "created_at"]

    def validate_free_capacity_kg(self, value):
        if value <= 0:
            raise serializers.ValidationError("Capacity must be greater than zero.")
        return value

    def validate(self, attrs):
        from_city = attrs.get("from_city", getattr(self.instance, "from_city", None))
        to_city = attrs.get("to_city", getattr(self.instance, "to_city", None))
        if from_city and to_city and from_city == to_city:
            raise serializers.ValidationError("from_city and to_city must be different.")
        return attrs