# from .calendar import BlogHTMLCalendar
# from .filters import DreamFilter
from .models import *
from datetime import date
from django.contrib.postgres.search import SearchVector, SearchQuery
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.functions import TruncMonth
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.base import TemplateView


paginate_count = 5  # This is basically a global variable.
def paginate(queryset, request):
    paginator = Paginator(queryset, paginate_count)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)



def dreams_index(request):
    dreams = Dream.objects.all().order_by("-created_on")

    # Output to Template
    context = {
        "page_obj": paginate(dreams, request),
    }
    return render(request, "dreams/index.html", context)



def dream_detail(request, pk):
    try:
        dream = Dream.objects.get(pk=pk)

        # Output to Template
        dream_edit_url = reverse("admin:{}_{}_change"
                  .format(dream._meta.app_label, dream._meta.model_name), 
                  args=[dream.pk])

        context = {
            "site_title": dream.title,
            "page_title": '<a href="{}">{}</a>'.format(dream_edit_url, dream.title),
            "dream": dream,
        }
        return render(request, "dreams/dream_detail.html", context)

    except Dream.DoesNotExist:
        return render(None, "dreams/404.html", context={})


# Symbol view
def symbol_definition(request, symbol):
    dreams = Dream.objects.filter(
        symbols__name = symbol
        ).order_by("-created_on")

    # Output to Template
    symbol = Symbol.objects.get(name=symbol)
    symbol_edit_url = reverse("admin:{}_{}_change"
                  .format(symbol._meta.app_label, symbol._meta.model_name), 
                  args=[symbol.id])
    page_title = 'symbol: <a href="{}">{}</a>'.format(symbol_edit_url, symbol)

    context = {
        "site_title": 'Symbol: {}'.format(symbol),
        "page_title": page_title,
        "symbol": symbol,
        "page_obj": dreams,
    }
    return render(request, "dreams/symbol_definition.html", context)




