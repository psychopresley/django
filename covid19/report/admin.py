from django.contrib import admin
from .models import *
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


class YearListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('year')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'year'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('2021', _('2021')),
            ('2020', _('2020')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == '2021':
            return queryset.filter(month__startswith='2021')
        if self.value() == '2020':
            return queryset.filter(month__startswith='2020')


class MonthListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('month')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'month'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('jan', _('January')),
            ('feb', _('February')),
            ('mar', _('March')),
            ('apr', _('April')),
            ('may', _('May')),
            ('jun', _('June')),
            ('jul', _('July')),
            ('aug', _('August')),
            ('sept', _('September')),
            ('oct', _('October')),
            ('nov', _('November')),
            ('dec', _('December')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == 'jan':
            return queryset.filter(month__endswith='01')
        if self.value() == 'feb':
            return queryset.filter(month__endswith='02')
        if self.value() == 'mar':
            return queryset.filter(month__endswith='03')
        if self.value() == 'apr':
            return queryset.filter(month__endswith='04')
        if self.value() == 'mai':
            return queryset.filter(month__endswith='05')
        if self.value() == 'jun':
            return queryset.filter(month__endswith='06')
        if self.value() == 'jul':
            return queryset.filter(month__endswith='07')
        if self.value() == 'aug':
            return queryset.filter(month__endswith='08')
        if self.value() == 'sept':
            return queryset.filter(month__endswith='09')
        if self.value() == 'oct':
            return queryset.filter(month__endswith='10')
        if self.value() == 'nov':
            return queryset.filter(month__endswith='11')
        if self.value() == 'dec':
            return queryset.filter(month__endswith='12')


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):

    fieldsets = (
        ('General info', {
            'fields': ('name', 'region',)
        }),
        ('More options', {
            'classes': ('collapse',),
            'fields': (('latitude','longitude'),'internet_code','map_image',)
        }),
    )

    # fields = ('country','region',('latitude','longitude'),'internet_code','map_image')
    ordering = ['name']   # ordering = ['-country'] for descending order

    list_filter =('region',LocationListFilter,)
    list_display = ['__str__','region','_coordinates_']
    search_fields = ['name']

    actions_on_bottom = True
    actions_on_top = False


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


@admin.register(MonthReport)
class MonthReportAdmin(admin.ModelAdmin):
    ordering = ['-month','country']   # ordering = ['-country'] for descending order

    def region(self, obj):
        return obj.country.region

    fields = ('country', 'month', ('confirmed', 'confirmed_rank_region', 'confirmed_rank_world'),
             ('deaths', 'deaths_rank_region', 'deaths_rank_world'))

    region.short_description = 'region'

    list_display = ['__str__','region','month',]
    list_filter =[MonthListFilter,YearListFilter,]
    search_fields = ['country__name','country__region']


@admin.register(WeekReport)
class WeekReportAdmin(admin.ModelAdmin):
    ordering = ['-week','country']   # ordering = ['-country'] for descending order

    def region(self, obj):
        return obj.country.region

    fields = ('country', 'week', ('confirmed', 'confirmed_rank_region', 'confirmed_rank_world'),
             ('deaths', 'deaths_rank_region', 'deaths_rank_world'))

    region.short_description = 'region'

    list_display = ['__str__','region','week',]
    # list_filter =[MonthListFilter,YearListFilter,]
    search_fields = ['country__name','country__region']


@admin.register(UNData)
class UNDataAdmin(admin.ModelAdmin):
    ordering = ['country']   # ordering = ['-country'] for descending order

    fields = ('country', ('population', 'density'),
             ('pct_minus_fourteen', 'pct_plus_sixty'),
             ('population_male', 'population_female', 'sex_ratio'))

    list_display = ['__str__','year',]
    # list_filter =[MonthListFilter,YearListFilter,]
    search_fields = ['country']


@admin.register(ISOCodeData)
class ISOCodeDataAdmin(admin.ModelAdmin):
    ordering = ['geoip_name']   # ordering = ['-country'] for descending order

    fields = ('geoip_name', 'iso_code', 'un_name', 'country_name', 'geoname_id')

    list_display = ['__str__','iso_code','un_name','country_name']
    # list_filter =[MonthListFilter,YearListFilter,]
    search_fields = ['geoip_name','iso_code','un_name','country_name']


@admin.register(ConfigReport)
class ConfigReportAdmin(admin.ModelAdmin):
    ordering = ['var_name']   # ordering = ['-country'] for descending order

    fields = ('var_name', ('file_path', 'file_name'),
             ('db_delete', 'db_update', 'db_reload'))

    #list_display = ['__str__','region','week',]
    # list_filter =[MonthListFilter,YearListFilter,]
    # search_fields = ['country__name','country__region']
