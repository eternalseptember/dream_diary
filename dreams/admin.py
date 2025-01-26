from .models import *
from django.contrib import admin
from django.db.models import Count
from django.template.defaultfilters import truncatechars
from django.urls import reverse
from django.utils.html import format_html
from markdownx.admin import MarkdownxModelAdmin



# Adds five extra rows of symbolism when adding or editing a dream.
class Symbolism_Inline(admin.TabularInline):
    model = Symbolism
    extra = 5


@admin.register(Symbol)
class SymbolAdmin(admin.ModelAdmin):
    list_display = ["name", "dreams_count", "get_description", "view_symbol"]
    ordering = ["name"]
    list_per_page = 20

    # When adding or editing a symbol.
    readonly_fields = ["get_dreams", "view_symbol"]


    # Gets the number of dreams in a symbol and make this column sortable.
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(dreams_count=Count("dreams"))

    @admin.display(description="# of dreams")
    def dreams_count(self, obj):
        return obj.dreams_count
    dreams_count.admin_order_field = "dreams_count"


    # Shows a truncated description.
    @admin.display(description="description")
    def get_description(self, obj):
        return truncatechars(obj.description, 35)


    # Generates a list of links to dreams under a symbol.
    # 'dreams' in dreams.all() is the related_name of the model dreams.symbols.
    @admin.display(description="dreams")
    def get_dreams(self, obj):
        return self.links_to_dreams(obj.dreams.all().order_by("-created_on"))
    
    @classmethod
    def links_to_dreams(cls, objects_list):
        dreams_list = '<ol class="symbol_dreams_list">'

        for dream in objects_list:
            link = reverse("admin:{}_{}_change"
                  .format(dream._meta.app_label, dream._meta.model_name), 
                  args=[dream.id])
            dreams_list += '<li><a href="{}">{}</a></li>'.format(link, dream.title)
        
        dreams_list += '</ol>'
        return format_html(dreams_list)
    

    # Link to the public symbol page from admin.
    def view_symbol(self, obj):
        link_url = reverse("symbol_definition", kwargs={"symbol": obj.name})
        link = '<a href="{}" target="_blank">view</a>'.format(link_url)
        return format_html(link)


    # Resolves the error message when creating a new symbol,
    # because there is no link to the symbol yet.
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["get_dreams", "view_symbol"]
        else:
            return []



@admin.register(Dream)
class DreamAdmin(MarkdownxModelAdmin):
    list_display = ["title", "created_on", "last_modified", "view_dream"]
    ordering = ["-created_on"]
    list_per_page = 20
    actions_on_top = False
    actions_on_bottom = True
    search_fields= ["title"]
    list_filter = ["created_on", "last_modified"]

    # When adding or editing a dream.
    readonly_fields = ["view_dream"]
    inlines = [Symbolism_Inline]


    # Link to the published dream from admin.
    def view_dream(self, obj):
        link_url = reverse("dream_detail", kwargs={"pk": obj.id})
        link = '<a href="{}" target="_blank">view</a>'.format(link_url)
        return format_html(link)

    # Resolves the error message when creating a new dream
    # because there is no link to the published dream yet.
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["view_dream"]
        else:
            return []


@admin.register(Symbolism)
class SymbolismAdmin(admin.ModelAdmin):
    list_display = ["get_symbol", "get_dream", "get_comment"]
    fields = ["symbol", "dream", "comment"]
    readonly_fields = ["symbol", "dream"]
    actions = None


    # Disables the add functionality
    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description="symbol")
    def get_symbol(self, obj):
        link_url = reverse("admin:{}_{}_change"
                     .format(obj.symbol._meta.app_label, obj.symbol._meta.model_name), args=[obj.symbol.id])
        link_text = truncatechars(obj.symbol, 20)
        link = '<a href="{}">{}</a>'.format(link_url, link_text)
        return format_html(link)
    
    @admin.display(description="dream")
    def get_dream(self, obj):
        link_url = reverse("admin:{}_{}_change"
                     .format(obj.dream._meta.app_label, obj.dream._meta.model_name), args=[obj.dream.id])
        link_text = truncatechars(obj.dream, 20)
        link = '<a href="{}">{}</a>'.format(link_url, link_text)
        return format_html(link)

    @admin.display(description="comment")
    def get_comment(self, obj):
        link_url = reverse("admin:{}_{}_change"
                     .format(obj._meta.app_label, obj._meta.model_name), args=[obj.id])
        link_text = truncatechars(obj.comment, 40)
        link = '<a href="{}">{}</a>'.format(link_url, link_text)
        return format_html(link)







