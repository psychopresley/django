from django.db import models

# Create your models here.

class Country(models.Model):
    name = models.CharField(max_length=60,unique=True,default='undefined')

    def __str__(self):
        return self.name


class CountryInfo(models.Model):
    country = models.OneToOneField(Country, on_delete=models.CASCADE, primary_key=True,)
    latitude = models.FloatField(default=90)
    longitude = models.FloatField(default=0)
    region = models.CharField(max_length=30)

    def __str__(self):
        return self.country.name

    def _lat_(self):
        return self.latitude

    def _long_(self):
        return self.longitude

    def _region_(self):
        return self.region

    def _coordinates_(self):
        lat = str(abs(self.latitude)) + '°'
        long = str(abs(self.longitude)) + '°'

        if self.latitude < 0:
            lat_suffix = 'S'
        elif self.latitude > 0:
            lat_suffix = 'N'

        if self.longitude < 0:
            long_suffix = 'W'
        elif self.longitude > 0:
            long_suffix = 'E'

        return '%s, %s' % (lat + lat_suffix, long + long_suffix)


class StatusReport(models.Model):
    country = models.OneToOneField(Country, on_delete=models.CASCADE, primary_key=True,)
    confirmed = models.IntegerField()
    confirmed_new = models.IntegerField()
    confirmed_pct_change = models.FloatField()
    confirmed_rank_region = models.IntegerField()
    confirmed_rank_world = models.IntegerField()
    deaths = models.IntegerField()
    deaths_new = models.IntegerField()
    deaths_pct_change = models.FloatField()
    deaths_rank_region = models.IntegerField()
    deaths_rank_world = models.IntegerField()
    recovered = models.IntegerField(default=0)
    recovered_new = models.IntegerField()
    recovered_pct_change = models.FloatField()
    recovered_rank_region = models.IntegerField()
    recovered_rank_world = models.IntegerField()
    active = models.IntegerField(default=0)
    active_new = models.IntegerField()
    active_pct_change = models.FloatField()
    active_rank_region = models.IntegerField()
    active_rank_world = models.IntegerField()

    def __str__(self):
        return self.country


class WeekReport(models.Model):
    country = models.ManyToManyField(Country)
    week = models.CharField(max_length=2)
    year = models.CharField(max_length=4)
    confirmed = models.IntegerField()
    deaths = models.IntegerField()
    recovered = models.IntegerField(default=0)
    active = models.IntegerField(default=0)

    def __str__(self):
        return '%s %s - %s' % (self.country, self.week, self.year)


class MonthReport(models.Model):
    country = models.ManyToManyField(Country)
    month = models.CharField(max_length=10)
    year = models.CharField(max_length=4)
    confirmed = models.IntegerField()
    deaths = models.IntegerField()
    recovered = models.IntegerField(default=0)
    active = models.IntegerField(default=0)

    def __str__(self):
        return '%s %s - %s' % (self.country, self.month, self.year)


class DateReport(models.Model):
    country = models.ManyToManyField(Country)
    date = models.DateField()
    confirmed = models.IntegerField()
    deaths = models.IntegerField()
    recovered = models.IntegerField(default=0)
    active = models.IntegerField(default=0)

    def __str__(self):
        return '%s - %s' % (self.country, str(self.date))
