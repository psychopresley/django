from django.contrib import admin
from report.models import Country, CountryInfo, DateReport

# Register your models here.
admin.site.register(Country)
admin.site.register(CountryInfo)
admin.site.register(DateReport)
