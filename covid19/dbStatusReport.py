# To execute this file in the python shell just run the following
# command line: exec(open('db_StatusReport.py').read())

import os
import django
from pandas import read_csv
from report.models import Country, StatusReport

os.environ.setdefault('DJANGO_SETTINGS_MODULE','covid19.settings')
django.setup()

try:
    option_select = input('Select what you wish to do with models.StatusReport objects (1 = del / 2 = add / any other key = quit):')

    if option_select == '1':
        confirm_delete = input('This will erase all entries in models.StatusReport. Are you sure? [y/n]')

        if confirm_delete == 'y':
            StatusReport.objects.all().delete()
            print('All entries in models.StatusReport deleted succesfully!')
        else:
            print('No modifications on database.')
            pass
    elif option_select == '2':
        print('Reading status_report.csv file')
        status_table = read_csv('status_report.csv')
        countries_list = status_table['Country/Region'].unique()

        print('number of countries in the list: %s' % len(countries_list))
        x=input('Do you wish to add all countries in the list to models.StatusReport? [y/n]')

        if x=='n':
            print('No files were added in the database')
            pass
        elif x=='y':
            print('Inserting all countries in the list to models.StatusReport')

            for item in countries_list:
                country = Country.objects.filter(name=item)
                if country.exists():
                    info = status_table.loc[status_table['Country/Region']==item]

                    entry = StatusReport.objects.get_or_create(country=country[0],
                                                               date=info.date_modified.values[0],
                                                               confirmed=int(info.Confirmed.values[0]),
                                                               confirmed_new=int(info.Confirmed_new_cases.values[0]),
                                                               confirmed_pct_change=float(info['Confirmed_daily_%inc_by_country'].values[0]),
                                                               confirmed_rank_region=int(info.Confirmed_rank_in_region.values[0]),
                                                               confirmed_rank_world=int(info.Confirmed_rank_in_world.values[0]),
                                                               confirmed_new_rank_region=int(info.Confirmed_new_cases_rank_in_region.values[0]),
                                                               confirmed_new_rank_world=int(info.Confirmed_new_cases_rank_in_world.values[0]),
                                                               deaths=int(info.Deaths.values[0]),
                                                               deaths_new=int(info.Deaths_new_cases.values[0]),
                                                               deaths_pct_change=float(info['Deaths_daily_%inc_by_country'].values[0]),
                                                               deaths_rank_region=int(info.Deaths_rank_in_region.values[0]),
                                                               deaths_rank_world=int(info.Deaths_rank_in_world.values[0]),
                                                               deaths_new_rank_region=int(info.Deaths_new_cases_rank_in_region.values[0]),
                                                               deaths_new_rank_world=int(info.Deaths_new_cases_rank_in_world.values[0]),
                                                               recovered=int(info.Recovered.values[0]),
                                                               recovered_new=int(info.Recovered_new_cases.values[0]),
                                                               recovered_pct_change=float(info['Recovered_daily_%inc_by_country'].values[0]),
                                                               recovered_rank_region=int(info.Recovered_rank_in_region.values[0]),
                                                               recovered_rank_world=int(info.Recovered_rank_in_world.values[0]),
                                                               recovered_new_rank_region=int(info.Recovered_new_cases_rank_in_region.values[0]),
                                                               recovered_new_rank_world=int(info.Recovered_new_cases_rank_in_world.values[0]),
                                                               active=int(info.Active.values[0]),
                                                               active_new=int(info.Active_new_cases.values[0]),
                                                               active_pct_change=float(info['Active_daily_%inc_by_country'].values[0]),
                                                               active_rank_region=int(info.Active_rank_in_region.values[0]),
                                                               active_rank_world=int(info.Active_rank_in_world.values[0]),
                                                               active_new_rank_region=int(info.Active_new_cases_rank_in_region.values[0]),
                                                               active_new_rank_world=int(info.Active_new_cases_rank_in_world.values[0]))[0]

                    entry.save()
                    print('{} inserted into models.StatusReport'.format(item))
                else:
                    print(item + ' is not on StatusReport.models')
    else:
        pass

    print('Script executed succesfully!')
except:
    print('Something went wrong! The script was not executed')
finally:
    print('End of execution of the populate_StatusReport.py script')
