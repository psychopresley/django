# To execute this file in the python shell just run the following
# command line: exec(open('populate_CountryInfo.py').read())

import os
import django
from pandas import read_csv
from report.models import Country

os.environ.setdefault('DJANGO_SETTINGS_MODULE','covid19.settings')
django.setup()

try:
    print('Reading flourish.csv file')
    countries_table = read_csv('flourish.csv')
    countries_list = countries_table['Country'].unique()

    print(countries_table)
    print('number of countries in the list: %s' % len(countries_list))

    x=input('Do you wish to add all countries in the list to models.DateReport? [y/n]')
    if x=='n':
        print('No files were added in the database')
        pass
    elif x=='y':
        print('Inserting all countries in the list to models.CountryInfo')

        for item in countries_list:
            country = Country.objects.filter(name=item)
            if country.exists():
                country_region = countries_table.loc[countries_table['Country']==item].Region.values[0]
                country_lat = countries_table.loc[countries_table['Country']==item].Latitude.values[0]
                country_long = countries_table.loc[countries_table['Country']==item].Longitude.values[0]

                entry = CountryInfo.objects.get_or_create(country=country[0],
                                                          latitude=float(country_lat),
                                                          longitude=float(country_long),
                                                          region=country_region)[0]
                entry.save()

                print(item + ' inserted into models.CountryInfo')

    else:
        pass

    print('Script executed succesfully!')
except:
    print('Something went wrong! The script was not executed')
finally:
    print('End of execution of the populate_CountryInfo.py script')
