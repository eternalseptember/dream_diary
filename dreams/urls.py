from django.urls import path
from . import views


urlpatterns = [
    path("", views.dreams_index, name="dreams_index"),
    path("dream/<int:pk>/", views.dream_detail, name="dream_detail"),
    path("symbol/<symbol>/", views.symbol_definition, name="symbol_definition"),
    path("search/", views.dreams_search, name="dreams_search"),
]
