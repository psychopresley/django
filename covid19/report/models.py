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



class CountryReport(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    date = models.DateField()
    confirmed = models.IntegerField()
    deaths = models.IntegerField()
    recovered = models.IntegerField(default=0)
    active = models.IntegerField(default=0)

    def __str__(self):
        return '%s - %s' % (self.country, str(self.date))
