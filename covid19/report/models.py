from django.db import models

# Create your models here.

class Country(models.Model):
    name = models.CharField(max_length=60,unique=True,default='undefined')

    def __str__(self):
        return self.name


class CountryInfo(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    region = models.CharField(max_length=30)

    def __str__(self):
        return self.country


class CountryReport(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    date = models.DateField()
    confirmed = models.IntegerField()
    deaths = models.IntegerField()
    recovered = models.IntegerField(default=0)
    active = models.IntegerField(default=0)

    def __str__(self):
        return '%s %s' % (self.country, str(self.date))
