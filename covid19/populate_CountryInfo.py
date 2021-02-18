# To execute this file in the python shell just run the following
# command line: exec(open('populate_CountryInfo.py').read())

import os
import django
from pandas import read_csv
from report.models import Country, CountryInfo

os.environ.setdefault('DJANGO_SETTINGS_MODULE','covid19.settings')
django.setup()

try:
    option_select = input('Select what you wish to do with models.CountryInfo objects (1 = del / 2 = add / any other key = quit):')

    if option_select == '1':
        confirm_delete = input('This will erase all entries in models.CountryInfo. Are you sure? [y/n]')

        if confirm_delete == 'y':
            CountryInfo.objects.all().delete()
            print('All entries in models.CountryInfo deleted succesfully!')
        else:
            print('No modifications on database.')
            pass
    elif option_select == '2':
        print('Reading flourish.csv file')
        countries_table = read_csv('flourish.csv')
        countries_list = countries_table['Country'].unique()

        print('number of countries in the list: %s' % len(countries_list))
        x=input('Do you wish to add all countries in the list to models.CountryInfo? [y/n]')

        if x=='n':
            print('No files were added in the database')
            pass
        elif x=='y':
            print('Inserting all countries in the list to models.CountryInfo')

            for item in countries_list:
                country = Country.objects.filter(name=item)
                if country.exists():
                    info = countries_table.loc[countries_table['Country']==item]

                    entry = CountryInfo.objects.get_or_create(country=country[0],
                                                              latitude=float(info.Latitude.values[0]),
                                                              longitude=float(info.Longitude.values[0]),
                                                              region=info.Region.values[0],
                                                              internet_code=info.internet_code.values[0],
                                                              map_image=info.map_image.values[0])[0]
                    entry.save()

                    print(item + ' inserted into models.CountryInfo')
        else:
            pass
    else:
        print('Exit script!')
        pass

    print('Script executed succesfully!')
except:
    print('Something went wrong! The script was not executed')
finally:
    print('End of execution of the populate_CountryInfo.py script')
