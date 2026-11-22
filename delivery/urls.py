from django.urls import path

from . import views

urlpatterns = [
    path("parcels/", views.parcel_list),
    path("parcels/<int:id>/", views.parcel_detail),
]
