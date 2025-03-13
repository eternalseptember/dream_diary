from .calendar import HTMLCalendar
from .filters import Dream_Filter
from .models import *
from datetime import date
from django.contrib.postgres.search import SearchVector, SearchQuery
from django.core.paginator import Paginator
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



def dreams_search(request):
    query = request.GET.get("q")

    if query:
        # Basic search with postgres.
        search_results = Dream.objects.annotate(
            search=SearchVector("title", "recollection", "preoccupation", "interpretation")
            ).filter(search=SearchQuery(query))

    else:
        search_results = Dream.objects.none()

    # Output to Template
    context = {
        "site_title": 'Search: {}'.format(query),
        "page_title": 'search: {}'.format(query),
        "page_obj": paginate(search_results, request),
        "query": query,
    }
    return render(request, "dreams/search_results.html", context)



def advanced_search(request):
    queryset = Dream.objects.all()
    selected_symbols = request.GET.getlist("symbols")  # This is getlist instead of regular get!
    dream_filter = Dream_Filter(request.GET, selected_symbols=selected_symbols, queryset=queryset)

    """
    THIS SECTION NEEDS CAREFUL ATTENTION!
    FIX THE FIELD NAMES AFTER MODIFYING FILTERS!

    This section makes the advanced search page show *NOTHING* instead
    of *EVERYTHING* if there are no filters applied.

    This combined with the qs override in the filter (filters.py) makes
    the advanced search page show no posts when first loading into the
    page and when there's an invalid filter applied.
    """
    s1 = request.GET.get("title__icontains")  # used for highlighting
    s2 = request.GET.get("recollection__icontains")  # used for highlighting
    s3 = request.GET.get("preoccupation__icontains")  # used for highlighting
    s4 = request.GET.get("interpretation__icontains")  # used for highlighting
    s5 = request.GET.get("created_on__date")
    s6 = request.GET.get("created_on__date__gte")
    s7 = request.GET.get("created_on__date__lte")
    s8 = selected_symbols  # being passed to Dream_Filter object for filtering
    s9 = request.GET.get("anniversary_date")

    # Omitting a check for the custom filters ("and_symbols" and "sort_how").
    # If those are the only options selected, then return nothing.
    valid_requests = [s1, s2, s3, s4, s5, s6, s7, s8, s9]
    if any(valid_requests):
        search_results = dream_filter.qs
    else:
        search_results = Dream.objects.none()


    # Output to Template
    # Get symbol names from ID to make highlighting easier.
    query_symbols = [Symbol.objects.get(id=symbol_id).name for symbol_id in s8]

    context = {
        "site_title": 'Advanced Search',
        "form": dream_filter.form,
        "page_obj": paginate(search_results, request),
        "query_title": s1,  # for highlighting
        "query_recollection": s2,  # for highlighting
        "query_preoccupation": s3,  # for highlighting
        "query_interpretation": s4,  # for highlighting
        "query_symbols": query_symbols,  # for highlighting
    }
    return render(request, "dreams/advanced_search.html", context)



class ArchiveTimeView(TemplateView):
    """
    The master view that the daily, monthly, and yearly archives inherit from.
    """
    def get_prev_and_next(self, **kwargs):
        """
        prev_link, this_link, next_link are lists in the order of [year, month, day].
        Returns a list of [prev_link, this_link, next_link].
        """	
        this_link = list(kwargs.values())
        this_index = self.dates_list.index(this_link)

        # Previous (unit of time), skipping over empty (unit of time).
        prev_index = this_index - 1
        prev_link = self.dates_list[prev_index] if self.is_valid_index(prev_index) else None

        # Next (unit of time), skipping over empty (unit of time).
        next_index = this_index + 1
        next_link = self.dates_list[next_index] if self.is_valid_index(next_index) else None

        return [prev_link, this_link, next_link]

    def is_valid_index(self, index):
        return (0 <= index) and (index < len(self.dates_list))



class ArchiveDayView(ArchiveTimeView):
    template_name = "dreams/archive_day.html"

    def get_context_data(self, **kwargs):
        year = self.kwargs["year"]
        month = self.kwargs["month"]
        day = self.kwargs["day"]
        day_date = date(year, month, day)

        search_results = Dream.objects.filter(
            created_on__date = day_date
            ).order_by("-created_on")

        # Steps for nav links
        dates = Dream.objects.dates("created_on", "day", "ASC")
        self.dates_list = [[date.year, date.month, date.day] for date in dates]
        nav_links = self.get_prev_and_next(**kwargs)

        # Output to Template
        day_date = day_date.strftime("%b %-d, %Y")

        context = {
            "site_title": day_date,
            "page_title": day_date,
            "page_obj": search_results,
            "prev_day": nav_links[0],
            "this_day": nav_links[1],
            "next_day": nav_links[2],
        }
        return context



class ArchiveMonthView(ArchiveTimeView):
    template_name = "dreams/archive_month.html"

    def get_context_data(self, **kwargs):
        year = self.kwargs["year"]
        month = self.kwargs["month"]

        search_results = Dream.objects.filter(
            created_on__year = year,
            created_on__month = month
            ).order_by("-created_on")

        # Steps for nav links
        dates = Dream.objects.dates("created_on", "month", "ASC")
        self.dates_list = [[date.year, date.month] for date in dates]
        nav_links = self.get_prev_and_next(**kwargs)

        # Output to Template
        month_date = date(year, month, 1).strftime("%B %Y")

        context = {
            "site_title": month_date,
            "page_title": month_date,
            "page_obj": search_results,
            "prev_month": nav_links[0],
            "this_month": nav_links[1],
            "next_month": nav_links[2],
        }
        return context



class ArchiveYearView(ArchiveTimeView):
    template_name = "dreams/archive_year.html"

    def get_context_data(self, **kwargs):
        year = self.kwargs["year"]

        dreams_list = Dream.objects.filter(
            created_on__year = year
            ).order_by("created_on")

        search_results = dreams_list.annotate(month=TruncMonth("created_on"))
        cal = HTMLCalendar(year, dreams_list).print_year()

        # Steps for nav links
        dates = Dream.objects.dates("created_on", "year", "ASC")
        self.dates_list = [[date.year] for date in dates]
        nav_links = self.get_prev_and_next(**kwargs)

        # Output to Template
        context = {
            "site_title": 'Year {}'.format(year),
            "page_obj": search_results,
            "prev_year": nav_links[0],
            "this_year": nav_links[1],
            "next_year": nav_links[2],
            "cal": cal,
        }
        return context



class ArchiveView(TemplateView):
    template_name = "dreams/archive.html"

    def get_context_data(self, **kwargs):
        dates = Dream.objects.dates("created_on", "year", "DESC")
        years = [date.year for date in dates]

        # Output to Template
        context = {
            "site_title": 'Archives',
            "page_title": 'Archives',
            "years": years,
        }
        return context




