from .models import *
from django.db.models.functions import ExtractMonth, ExtractDay
from django.forms import CheckboxInput
import django_filters
from django_filters import BooleanFilter, ChoiceFilter, DateFilter, ModelMultipleChoiceFilter


class Dream_Filter(django_filters.FilterSet):
    """
    This is the Advanced Search form.
    """
    date_sort_choices=[
        ('desc', ('Desc (newest first)')),
        ('asc', ('Asc (oldest first)'))
        ]

    # Custom non-model fields
    anniversary_date = DateFilter(label="Created yearly on", method="anniversary_search")
    symbols = ModelMultipleChoiceFilter(
        queryset=Symbol.objects.all().order_by("name"), 
        field_name="symbols",
        lookup_expr="exact",
        )
    and_symbols = BooleanFilter(label="Symbols AND?", widget=CheckboxInput, method="and_search")
    sort_how = ChoiceFilter(choices=date_sort_choices, label="Sort by date?", empty_label="----", method="sort_by_date")


    class Meta:
        model = Dream
        fields = {
            "title": ["icontains"],
            "recollection": ["icontains"],
            "preoccupation": ["icontains"],
            "interpretation": ["icontains"],
            "created_on": ["date", "date__gte", "date__lte"],
            }


    def __init__(self, *args, **kwargs):
        self.selected_symbols = kwargs.pop('selected_symbols')
        super(Dream_Filter, self).__init__(*args, **kwargs)
        self.filters["created_on__date"].label="Created on"
        self.filters["created_on__date__gte"].label="Created on or after"
        self.filters["created_on__date__lte"].label="Created on or before"


    def anniversary_search(self, queryset, field_name, value):
        """
        "field_name" is "anniversary_date".
        "value" is a date, whose year will be ignored.
        """
        if value:
            month = ExtractMonth(value)
            day = ExtractDay(value)
            print('anniversary month: {} day {}'.format(month, day))
            return queryset.filter(created_on__month = month, created_on__day = day)
        return queryset


    def and_search(self, queryset, field_name, value):
        """
        "field_name" is "and_symbols".
        "value" is boolean True or False.
        If False, then return the normal search results (which is done with boolean 'OR').
        If True, then run boolean 'AND' on the queryset with all of the selected symbols 
        (which are passed as symbols__id).
        """
        if value is False:
            return queryset
        for selected_symbol in self.selected_symbols:
            queryset = queryset.filter(symbols__id = selected_symbol)
        return queryset


    def sort_by_date(self, queryset, field_name, value):
        """
        "field_name" is "sort_how".
        "value" could be "desc", "asc", or the empty choice, presumbly None,
        which sorts by post.id by default.
        """
        if value == "desc":
            return queryset.order_by("-created_on")
        elif value == "asc":
            return queryset.order_by("created_on")
        return queryset


    # This override so that the queryset returns *NOTHING* 
    # instead of *EVERYTHING* if there's an invalid filter.
    @property
    def qs(self):
        if not hasattr(self, '_qs'):
            qs = self.queryset.all()
            if self.is_bound:
                if self.form.is_valid():
                    qs = self.filter_queryset(qs)
                else:
                    qs = self.queryset.none()
            self._qs = qs
        return self._qs
