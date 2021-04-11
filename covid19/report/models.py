from django.db import models
from django.conf import settings
from django.utils import timezone
import datetime
import os

# Create your models here.

class ConfigReport(models.Model):
    var_name = models.CharField(max_length=30,primary_key=True,default='dbconfig_')
    base_file = models.FilePathField(path=settings.DATA_FILE_DIR)
    aux_file_one = models.FilePathField(path=settings.DATA_FILE_DIR)
    aux_file_two = models.FilePathField(path=settings.DATA_FILE_DIR)
    date = models.CharField(max_length=60,default='not specified')
    TASK_CHOICES = (
        (0,'delete'),
        (1,'update'),
        (2,'reload'),
    )
    task = models.IntegerField(default=1, choices=TASK_CHOICES)
    confirm_delete = models.BooleanField(default=True)
    auto_exec = models.BooleanField(default=True)

    def __str__(self):
        return self.var_name


class ISOCodeData(models.Model):
    geoname_id = models.IntegerField(primary_key=True,default=0)
    iso_code = models.CharField(max_length=2,default='00')
    geoip_name = models.CharField(max_length=60,default='undefined')
    un_name = models.CharField(max_length=60,default='undefined')
    country_name = models.CharField(max_length=60,default='undefined')

    def __str__(self):
        return self.geoip_name


class UNData(models.Model):
    country = models.CharField(max_length=60,primary_key=True,default='undefined')
    year = models.CharField(max_length=4,default='2020')
    population = models.FloatField(default=1e4)
    density = models.FloatField(default=1.0)
    population_male = models.FloatField(default=1e4)
    population_female = models.FloatField(default=1e4)
    sex_ratio = models.FloatField(default=1.0)
    pct_minus_fourteen = models.FloatField(default=1)
    pct_plus_sixty = models.FloatField(default=1)

    def __str__(self):
        return self.country


class Country(models.Model):
    name = models.CharField(max_length=60,primary_key=True,default='undefined')
    latitude = models.FloatField(default=90)
    longitude = models.FloatField(default=0)
    region = models.CharField(max_length=30)
    internet_code = models.CharField(max_length=2,default='br')
    map_image = models.URLField(max_length=264,default='www.google.com')

    def __str__(self):
        return self.name

    def _coordinates_(self):
        lat = str(abs(self.latitude)) + '°'
        long = str(abs(self.longitude)) + '°'

        long_suffix=''
        lat_suffix=''

        if self.latitude < 0:
            lat_suffix = 'S'
        elif self.latitude > 0:
            lat_suffix = 'N'

        if self.longitude < 0:
            long_suffix = 'W'
        elif self.longitude > 0:
            long_suffix = 'E'

        return '({}, {})'.format(lat + lat_suffix, long + long_suffix)


class StatusReport(models.Model):
    country = models.OneToOneField(Country, on_delete=models.CASCADE, primary_key=True,)
    date = models.DateField(default=datetime.date.today)
    db_update = models.DateField(default=datetime.date.today)
    confirmed = models.IntegerField()
    confirmed_new = models.IntegerField()
    confirmed_new_short_avg = models.FloatField(default=0.0)
    confirmed_new_medium_avg = models.FloatField(default=0.0)
    confirmed_new_long_avg = models.FloatField(default=0.0)
    confirmed_new_pct_change = models.FloatField(default=100)
    confirmed_pct_change = models.FloatField()
    confirmed_rank_region = models.IntegerField()
    confirmed_rank_world = models.IntegerField()
    confirmed_new_rank_region = models.IntegerField(default=0)
    confirmed_new_rank_world = models.IntegerField(default=0)
    confirmed_by_hundreds = models.FloatField(default=1)
    confirmed_by_hundreds_rank_region = models.IntegerField(default=1)
    confirmed_by_hundreds_rank_world = models.IntegerField(default=1)
    deaths = models.IntegerField()
    deaths_new = models.IntegerField()
    deaths_new_short_avg = models.FloatField(default=0.0)
    deaths_new_medium_avg = models.FloatField(default=0.0)
    deaths_new_long_avg = models.FloatField(default=0.0)
    deaths_new_pct_change = models.FloatField(default=100)
    deaths_pct_change = models.FloatField()
    deaths_rank_region = models.IntegerField()
    deaths_rank_world = models.IntegerField()
    deaths_new_rank_region = models.IntegerField(default=0)
    deaths_new_rank_world = models.IntegerField(default=0)
    deaths_by_hundreds = models.FloatField(default=1)
    deaths_by_hundreds_rank_region = models.IntegerField(default=1)
    deaths_by_hundreds_rank_world = models.IntegerField(default=1)
    recovered = models.IntegerField(default=0)
    recovered_new = models.IntegerField()
    recovered_new_short_avg = models.FloatField(default=0.0)
    recovered_new_medium_avg = models.FloatField(default=0.0)
    recovered_new_long_avg = models.FloatField(default=0.0)
    recovered_pct_change = models.FloatField()
    recovered_rank_region = models.IntegerField()
    recovered_rank_world = models.IntegerField()
    recovered_new_rank_region = models.IntegerField(default=0)
    recovered_new_rank_world = models.IntegerField(default=0)
    recovered_by_hundreds = models.FloatField(default=1)
    recovered_by_hundreds_rank_region = models.IntegerField(default=1)
    recovered_by_hundreds_rank_world = models.IntegerField(default=1)
    active = models.IntegerField(default=0)
    active_new = models.IntegerField()
    active_new_short_avg = models.FloatField(default=0.0)
    active_new_medium_avg = models.FloatField(default=0.0)
    active_new_long_avg = models.FloatField(default=0.0)
    active_pct = models.FloatField(default=0)
    active_pct_change = models.FloatField()
    active_rank_region = models.IntegerField()
    active_rank_world = models.IntegerField()
    active_new_rank_region = models.IntegerField(default=0)
    active_new_rank_world = models.IntegerField(default=0)
    active_by_hundreds = models.FloatField(default=1)
    active_by_hundreds_rank_region = models.IntegerField(default=1)
    active_by_hundreds_rank_world = models.IntegerField(default=1)
    mortality = models.FloatField(default=0)
    mortality_quartile = models.CharField(max_length=35, default='4th quartile (very high mortality)')
    mortality_quartile_position = models.FloatField(default=50.0)
    mortality_rank_region = models.IntegerField(default=1000)
    mortality_rank_world = models.IntegerField(default=1000)

    def __str__(self):
        return self.country.name


class MonthReport(models.Model):
    country = models.ForeignKey(Country,on_delete=models.CASCADE,default='undefined')
    month = models.CharField(max_length=7,default='2000-01')
    confirmed = models.IntegerField(default=0)
    confirmed_pct_change = models.FloatField(default=0)
    confirmed_rank_region = models.IntegerField(default=0)
    confirmed_rank_world = models.IntegerField(default=0)
    deaths = models.IntegerField(default=0)
    deaths_pct_change = models.FloatField(default=0)
    deaths_rank_region = models.IntegerField(default=0)
    deaths_rank_world = models.IntegerField(default=0)
    days_in_month = models.IntegerField(default=30)
    last_update = models.DateField(default=datetime.date.today)


    def __str__(self):
        return self.country.name


class WeekReport(models.Model):
    country = models.ForeignKey(Country,on_delete=models.CASCADE,default='undefined')
    week = models.CharField(max_length=7,default='2000-01')
    confirmed = models.IntegerField(default=0)
    confirmed_pct_change = models.FloatField(default=0)
    confirmed_rank_region = models.IntegerField(default=0)
    confirmed_rank_world = models.IntegerField(default=0)
    deaths = models.IntegerField(default=0)
    deaths_pct_change = models.FloatField(default=0)
    deaths_rank_region = models.IntegerField(default=0)
    deaths_rank_world = models.IntegerField(default=0)
    last_update = models.DateField(default=datetime.date.today)


    def __str__(self):
        return self.country.name
#
#
# class DateReport(models.Model):
#     country = models.ManyToManyField(Country)
#     date = models.DateField()
#     confirmed = models.IntegerField()
#     deaths = models.IntegerField()
#     recovered = models.IntegerField(default=0)
#     active = models.IntegerField(default=0)
#
#     def __str__(self):
#         return '%s - %s' % (self.country, str(self.date))
