from django.urls import path

from . import views

urlpatterns = [
    path("parcels/", views.ParcelListCreateView.as_view()),
    path("parcels/<int:pk>/", views.ParcelDetailView.as_view()),
    path("cities/", views.CityListView.as_view()),
    path("cities/<int:pk>/parcels/", views.CityParcelListView.as_view()),
    path("trips/", views.TripListCreateView.as_view()),
    path("trips/<int:pk>/", views.TripDetailView.as_view()),
    path("trips/<int:pk>/stops/", views.TripStopListCreateView.as_view()),
]