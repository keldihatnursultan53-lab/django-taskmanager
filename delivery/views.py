import json
from decimal import Decimal, InvalidOperation

from django.contrib.auth import get_user_model
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import City, Parcel

User = get_user_model()

REQUIRED_FIELDS = [
    "sender", "from_city", "to_city", "title", "declared_contents",
    "weight_kg", "pickup_from", "deliver_by", "price", "is_declaration_confirmed",
]
DECIMAL_MAX_DIGITS = {"weight_kg": 6, "price": 10, "pickup_fee": 10}


def parcel_to_dict(parcel):
    return {
        "id": parcel.id,
        "sender": parcel.sender_id,
        "from_city": parcel.from_city_id,
        "to_city": parcel.to_city_id,
        "title": parcel.title,
        "declared_contents": parcel.declared_contents,
        "weight_kg": str(parcel.weight_kg),
        "size": parcel.size,
        "pickup_from": parcel.pickup_from.isoformat(),
        "deliver_by": parcel.deliver_by.isoformat(),
        "price": str(parcel.price),
        "allow_offers": parcel.allow_offers,
        "handover_method": parcel.handover_method,
        "pickup_address": parcel.pickup_address,
        "pickup_fee": str(parcel.pickup_fee),
        "is_declaration_confirmed": parcel.is_declaration_confirmed,
        "status": parcel.status,
        "created_at": parcel.created_at.isoformat(),
    }


def read_json(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    return data if isinstance(data, dict) else None


def to_decimal(value):
    if isinstance(value, bool):
        return None
    try:
        number = Decimal(str(value))
    except InvalidOperation:
        return None
    return number if number.is_finite() else None


def to_datetime(value):
    if not isinstance(value, str):
        return None
    try:
        result = parse_datetime(value)
    except ValueError:
        return None
    if result is not None and timezone.is_naive(result):
        result = timezone.make_aware(result)
    return result


def clean_decimal(field, raw, cleaned, errors):
    value = to_decimal(raw)
    if value is None:
        errors[field] = "Must be a number."
    elif abs(value) >= Decimal(10) ** (DECIMAL_MAX_DIGITS[field] - 2):
        errors[field] = "Number is too large."
    else:
        cleaned[field] = value.quantize(Decimal("0.01"))


def clean_parcel_data(data):
    errors = {}
    cleaned = {}

    for field in REQUIRED_FIELDS:
        if field not in data or data[field] in (None, ""):
            errors[field] = "This field is required."
    if errors:
        return None, errors

    for field, model in (("sender", User), ("from_city", City), ("to_city", City)):
        try:
            cleaned[field] = model.objects.get(pk=data[field])
        except (model.DoesNotExist, ValueError, TypeError):
            errors[field] = "Object with this id does not exist."

    for field, limit in (("title", 200), ("declared_contents", 5000)):
        value = data[field]
        if not isinstance(value, str) or not value.strip():
            errors[field] = "Must be a non-empty string."
        elif len(value) > limit:
            errors[field] = f"Must be at most {limit} characters."
        else:
            cleaned[field] = value.strip()

    for field in ("weight_kg", "price"):
        clean_decimal(field, data[field], cleaned, errors)

    for field in ("pickup_from", "deliver_by"):
        value = to_datetime(data[field])
        if value is None:
            errors[field] = "Must be a datetime like 2026-12-01T10:00:00+05:00."
        else:
            cleaned[field] = value

    if not isinstance(data["is_declaration_confirmed"], bool):
        errors["is_declaration_confirmed"] = "Must be true or false."
    else:
        cleaned["is_declaration_confirmed"] = data["is_declaration_confirmed"]

    if "size" in data:
        if data["size"] in Parcel.Size.values:
            cleaned["size"] = data["size"]
        else:
            errors["size"] = "Must be one of: " + ", ".join(Parcel.Size.values) + "."

    if "handover_method" in data:
        if data["handover_method"] in Parcel.HandoverMethod.values:
            cleaned["handover_method"] = data["handover_method"]
        else:
            errors["handover_method"] = "Must be one of: " + ", ".join(Parcel.HandoverMethod.values) + "."

    if "allow_offers" in data:
        if isinstance(data["allow_offers"], bool):
            cleaned["allow_offers"] = data["allow_offers"]
        else:
            errors["allow_offers"] = "Must be true or false."

    if "pickup_address" in data:
        if isinstance(data["pickup_address"], str) and len(data["pickup_address"]) <= 255:
            cleaned["pickup_address"] = data["pickup_address"].strip()
        else:
            errors["pickup_address"] = "Must be a string up to 255 characters."

    if "pickup_fee" in data:
        clean_decimal("pickup_fee", data["pickup_fee"], cleaned, errors)

    if errors:
        return None, errors
    return cleaned, None


@csrf_exempt
@require_http_methods(["GET", "POST"])
def parcel_list(request):
    if request.method == "GET":
        parcels = Parcel.objects.all()
        return JsonResponse([parcel_to_dict(p) for p in parcels], safe=False)

    data = read_json(request)
    if data is None:
        return JsonResponse({"error": "Request body must be a valid JSON object"}, status=400)
    cleaned, errors = clean_parcel_data(data)
    if errors:
        return JsonResponse({"errors": errors}, status=400)
    parcel = Parcel.objects.create(**cleaned)
    return JsonResponse(parcel_to_dict(parcel), status=201)


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def parcel_detail(request, id):
    try:
        parcel = Parcel.objects.get(pk=id)
    except Parcel.DoesNotExist:
        return JsonResponse({"error": "Parcel not found"}, status=404)

    if request.method == "GET":
        return JsonResponse(parcel_to_dict(parcel))

    if request.method == "DELETE":
        parcel.delete()
        return HttpResponse(status=204)

    data = read_json(request)
    if data is None:
        return JsonResponse({"error": "Request body must be a valid JSON object"}, status=400)
    cleaned, errors = clean_parcel_data(data)
    if errors:
        return JsonResponse({"errors": errors}, status=400)
    for field, value in cleaned.items():
        setattr(parcel, field, value)
    parcel.save()
    return JsonResponse(parcel_to_dict(parcel))