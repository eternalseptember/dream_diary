from django.urls import path
from . import views


urlpatterns = [
    path("", views.dreams_index, name="dreams_index"),
    path("dream/<int:pk>/", views.dream_detail, name="dream_detail"),
    path("symbol/<symbol>/", views.symbol_definition, name="symbol_definition"),
    path("search/", views.dreams_search, name="dreams_search"),
    path("advanced_search/", views.advanced_search, name="advanced_search"),
    path("archive/<int:year>/<int:month>/<int:day>/", views.ArchiveDayView.as_view(), name="archive_day"),
    path("archive/<int:year>/<int:month>/", views.ArchiveMonthView.as_view(), name="archive_month"),
    path("archive/<int:year>/", views.ArchiveYearView.as_view(), name="archive_year"),
    path("archives/", views.ArchiveView.as_view(), name="dreams_archives"),
]
