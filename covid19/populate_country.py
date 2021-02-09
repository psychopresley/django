# To execute this file in the python shell just run the following
# command line: exec(open('populate_country.py').read())

import os
import django
from pandas import read_csv
from report.models import Country

os.environ.setdefault('DJANGO_SETTINGS_MODULE','covid19.settings')
django.setup()

try:
    print('Reading countries.csv file')
    countries = read_csv('countries.csv');

    country_list = countries['Country/Region'].unique()
    print(country_list)
    print('number of countries in the list: %s' % len(country_list))

    x=input('Do you wish to add all countries in the list to models.Country? [y/n]')

    if x=='n':
        print('No files were added in the database')
    elif x=='y':
        print('Inserting all countries in the list to models.Country')

        for country in country_list:
            print('Inserting %s into models.Country' % country)

            entry = Country.objects.get_or_create(name=country)[0]
            entry.save()
    else:
        pass

    print('Script executed succesfully!')
except:
    print('Something went wrong! The script was not executed')
finally:
    print('End of execution of the populate_country.py script')
