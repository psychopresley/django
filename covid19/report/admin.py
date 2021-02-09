from django.contrib import admin
from report.models import Country, CountryInfo, CountryReport

# Register your models here.
admin.site.register(Country)
admin.site.register(CountryInfo)
admin.site.register(CountryReport)
