from django.urls import path

from . import views

urlpatterns = [
    path("parcels/", views.ParcelListCreateView.as_view()),
    path("parcels/<int:pk>/", views.ParcelDetailView.as_view()),
]