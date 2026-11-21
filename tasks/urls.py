from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('about/', views.about),
    path('health/', views.health),
    path('tasks/', views.task_list),
    path('tasks/<int:id>/', views.task_detail),
    path('echo/', views.echo),
]