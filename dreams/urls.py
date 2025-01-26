from django.urls import path
from . import views


urlpatterns = [
    path("", views.dreams_index, name="dreams_index"),
    path("dream/<int:pk>/", views.dream_detail, name="dream_detail"),
]
