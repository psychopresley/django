from django.contrib import admin
from .models import Country, CountryInfo, StatusReport, MonthReport
from django.utils.translation import gettext_lazy as _

admin.site.disable_action('delete_selected')

class LocationListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('location')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'location'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('south', _('Penguins, Kangoroos and sea lions')),
            ('north', _('Polar bears, seals and wolves')),
            ('eqt', _('Tropics')),
            ('east', _('East end boys')),
            ('west', _('West end girls')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == 'south':
            return queryset.filter(latitude__lte=-23)
        if self.value() == 'north':
            return queryset.filter(latitude__gte=23)
        if self.value() == 'eqt':
            return queryset.filter(latitude__lte=23,
                                   latitude__gte=-23)
        if self.value() == 'east':
            return queryset.filter(longitude__gt=0)
        if self.value() == 'west':
            return queryset.filter(longitude__lt=0)


@admin.register(CountryInfo)
class CountryInfoAdmin(admin.ModelAdmin):

    fieldsets = (
        ('General info', {
            'fields': ('country', 'region',)
        }),
        ('More options', {
            'classes': ('collapse',),
            'fields': (('latitude','longitude'),'internet_code','map_image',)
        }),
    )

    # fields = ('country','region',('latitude','longitude'),'internet_code','map_image')
    ordering = ['country']   # ordering = ['-country'] for descending order

    list_filter =('region',LocationListFilter,)
    list_display = ['__str__','region','_coordinates_']
    search_fields = ['country__name']

    actions_on_bottom = True
    actions_on_top = False


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    ordering = ['name']   # ordering = ['-name'] for descending order


@admin.register(StatusReport)
class StatusReportAdmin(admin.ModelAdmin):
    ordering = ['country']   # ordering = ['-country'] for descending order

    fieldsets = (
        ('General info', {
            'fields': ('country', 'date', ('confirmed', 'deaths'),('active', 'recovered'))
        }),
        ('Advanced options', {
            'description': 'information on data variation and rank',
            'classes': ('collapse',),
            'fields': (('confirmed_new', 'confirmed_rank_region', 'confirmed_rank_world'),
                       ('active_new', 'active_rank_region', 'active_rank_world'),
                       ('deaths_new', 'deaths_rank_region', 'deaths_rank_world'),
                       ('recovered_new', 'recovered_rank_region', 'recovered_rank_world'),)
        }),
    )

    list_display = ['__str__','date','confirmed']
