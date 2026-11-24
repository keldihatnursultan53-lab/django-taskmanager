from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.exceptions import ValidationError

from .models import City, Parcel, Trip, TripStop
from .serializers import CitySerializer, ParcelSerializer, TripSerializer, TripStopSerializer


class ParcelListCreateView(generics.ListCreateAPIView):
    queryset = Parcel.objects.all()
    serializer_class = ParcelSerializer


class ParcelDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Parcel.objects.all()
    serializer_class = ParcelSerializer


class CityListView(generics.ListAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer


class CityParcelListView(generics.ListAPIView):
    serializer_class = ParcelSerializer

    def get_queryset(self):
        city = get_object_or_404(City, pk=self.kwargs["pk"])
        return Parcel.objects.filter(from_city=city)


class TripListCreateView(generics.ListCreateAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer


class TripDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer


class TripStopListCreateView(generics.ListCreateAPIView):
    serializer_class = TripStopSerializer

    def get_trip(self):
        return get_object_or_404(Trip, pk=self.kwargs["pk"])

    def get_queryset(self):
        return TripStop.objects.filter(trip=self.get_trip())

    def perform_create(self, serializer):
        trip = self.get_trip()
        order = serializer.validated_data["order"]
        city = serializer.validated_data["city"]
        if TripStop.objects.filter(trip=trip, order=order).exists():
            raise ValidationError({"order": "A stop with this order already exists for this trip."})
        if city in (trip.from_city, trip.to_city):
            raise ValidationError({"city": "A stop must differ from the start and end cities of the trip."})
        serializer.save(trip=trip)