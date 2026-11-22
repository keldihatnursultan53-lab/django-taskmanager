from rest_framework import serializers

from .models import Parcel


class ParcelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcel
        fields = [
            "id",
            "sender",
            "from_city",
            "to_city",
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