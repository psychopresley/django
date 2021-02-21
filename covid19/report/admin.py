from django.contrib import admin
from report.models import Country, CountryInfo, StatusReport, MonthReport

# Register your models here.
admin.site.register(Country)
admin.site.register(CountryInfo)
admin.site.register(StatusReport)
admin.site.register(MonthReport)
