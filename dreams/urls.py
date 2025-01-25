from django.urls import path
from . import views


urlpatterns = [
    path("", views.dreams_index, name="dreams_index"),
]
