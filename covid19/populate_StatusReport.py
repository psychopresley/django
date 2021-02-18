# To execute this file in the python shell just run the following
# command line: exec(open('populate_StatusReport.py').read())

import os
import django
from pandas import read_csv
from report.models import Country, StatusReport

os.environ.setdefault('DJANGO_SETTINGS_MODULE','covid19.settings')
django.setup()

try:
    print('Reading status_report.csv file')
    status_table = read_csv('status_report.csv')
    countries_list = status_table['Country/Region'].unique()

    print('number of countries in the list: %s' % len(countries_list))

    x=input('Do you wish to add all countries in the list to models.StatusReport? [y/n]')
    if x=='n':
        print('No files were added in the database')
        StatusReport.objects.all().delete()
        pass
    elif x=='y':
        print('Inserting all countries in the list to models.StatusReport')

        for item in countries_list:
            country = Country.objects.filter(name=item)
            if country.exists():
                info = status_table.loc[status_table['Country/Region']==item]

                country_date = info.Date.values[0]
                country_confirmed = int(info.Confirmed.values[0])
                country_confirmed_new = int(info.Confirmed_new_cases.values[0])
                country_confirmed_pct_change = info['Confirmed_daily_%inc_by_country'].values[0]
                country_confirmed_rank_region = int(info.Confirmed_rank_in_region.values[0])
                country_confirmed_rank_world = int(info.Confirmed_rank_in_world.values[0])

                country_deaths = int(info.Deaths.values[0])
                country_deaths_new = int(info.Deaths_new_cases.values[0])
                country_deaths_pct_change = info['Deaths_daily_%inc_by_country'].values[0]
                country_deaths_rank_region = int(info.Deaths_rank_in_region.values[0])
                country_deaths_rank_world = int(info.Deaths_rank_in_world.values[0])

                country_recovered = int(info.Recovered.values[0])
                country_recovered_new = int(info.Recovered_new_cases.values[0])
                country_recovered_pct_change = info['Recovered_daily_%inc_by_country'].values[0]
                country_recovered_rank_region = int(info.Recovered_rank_in_region.values[0])
                country_recovered_rank_world = int(info.Recovered_rank_in_world.values[0])

                country_active = int(info.Active.values[0])
                country_active_new = int(info.Active_new_cases.values[0])
                country_active_pct_change = info['Active_daily_%inc_by_country'].values[0]
                country_active_rank_region = int(info.Active_rank_in_region.values[0])
                country_active_rank_world = int(info.Active_rank_in_world.values[0])

                entry = StatusReport.objects.get_or_create(country=country[0],
                                                           date=country_date,
                                                           confirmed=country_confirmed,
                                                           confirmed_new=country_confirmed_new,
                                                           confirmed_pct_change=float(country_confirmed_pct_change),
                                                           confirmed_rank_region=country_confirmed_rank_region,
                                                           confirmed_rank_world=country_confirmed_rank_world,
                                                           deaths=country_deaths,
                                                           deaths_new=country_deaths_new,
                                                           deaths_pct_change=float(country_deaths_pct_change),
                                                           deaths_rank_region=country_deaths_rank_region,
                                                           deaths_rank_world=country_deaths_rank_world,
                                                           recovered=country_recovered,
                                                           recovered_new=country_recovered_new,
                                                           recovered_pct_change=float(country_recovered_pct_change),
                                                           recovered_rank_region=country_recovered_rank_region,
                                                           recovered_rank_world=country_recovered_rank_world,
                                                           active=country_active,
                                                           active_new=country_active_new,
                                                           active_pct_change=float(country_active_pct_change),
                                                           active_rank_region=country_active_rank_region,
                                                           active_rank_world=country_active_rank_world)[0]

                entry.save()

                print('{} inserted into models.StatusReport'.format(item))
            else:
                print(item + ' is not on Country.models')
    else:
        pass

    print('Script executed succesfully!')
except:
    print('Something went wrong! The script was not executed')
finally:
    print('End of execution of the populate_StatusReport.py script')
