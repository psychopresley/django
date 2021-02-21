
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE','covid19.settings')
django.setup()

from pandas import read_json, read_csv
from report.models import Country, StatusReport

def main():
    def db_del(database,confirm_before=True):
        # This function delete all entries in "database" model

        flag = True

        if confirm_before:
            confirm_delete = input('This will erase all entries in models.StatusReport. Press "n" if you wish to skip delete or any other key to continue: ')

            if confirm_delete == 'n':
                flag = False
            else:
                pass

        if flag:
            database.objects.all().delete()
            print('All entries in models.{} deleted succesfully!'.format(database))
        else:
            print('No modifications on database.')
            pass

    def ordinal(x):
        # Function to be used in date format:
        if str(x)[-1] == '1':
            return 'st'
        elif str(x)[-1] == '2':
            return 'nd'
        elif str(x)[-1] == '3':
            return 'rd'
        else:
            return 'th'

    try:
        # In the config.csv file, on 'countryinfo_file' row of columns 'var':
        #  - aux1: Set 0, for delete all entries in database or 1 for add/update entries;
        #  - aux2: Set 0, for reload database from 'country_report.json' file or 1 for update existing entries;
        #  - aux3: Set 1, for confirmation need in case aux1 is set to 0;

        config_filepath = r"C:\Users\user\Documents\GitHub\django\covid19\static\report\config"

        if 'config.csv' in os.listdir(config_filepath):
            print('Reading configuration file')
            config = read_csv(os.path.join(config_filepath,'config.csv'),index_col='var').fillna('-')
        else:
    	    raise FileNotFoundError('No configuration file "config.csv" found.')

        task = config.loc['status_report'].aux1
        update = config.loc['status_report'].aux2
        confirm_value=config.loc['status_report'].aux3

        if not task:
            db_del(StatusReport,confirm_before=confirm_value)

        else:
            country_report = os.path.join(config.loc['status_report'].file_path,
                                              config.loc['status_report'].file_name)

            country_table_file = os.path.join(config.loc['countryinfo_file'].file_path,
                                              config.loc['countryinfo_file'].file_name)

            countries_table = read_csv(country_table_file,index_col='Country')

            # reading region dictionary:
            region_dict = countries_table['Region'].to_dict()

            print("Reading 'country_report.json' file")
            df = read_json(country_report)

            print("Generating status report table")
            df_aux = df.copy()[['Country/Region','Date']]

            df_aux['region'] = df_aux['Country/Region'].transform(lambda x: region_dict[x] if x in region_dict.keys() else x)

            column_names = ['Confirmed','Deaths','Active','Recovered']
            for column in column_names:
                column_new = column + '_new_cases'
                column_pct_change = column + '_daily_%inc_by_country'

                column_world_rank = column + '_rank_in_world'
                column_new_world_rank = column_new + '_rank_in_world'

                column_region_rank = column + '_rank_in_region'
                column_new_region_rank = column_new + '_rank_in_region'

                df_aux[column] = df[column]

                df_aux[column_new] = df[column_new]
                df_aux[column_pct_change] = df[column_pct_change]

                df_aux[column_world_rank]=df_aux.groupby('Date')[column].rank(method='min',ascending=False)
                df_aux[column_new_world_rank]=df_aux.groupby('Date')[column_new].rank(method='min',ascending=False)

                df_aux[column_region_rank]=df_aux.groupby(['Date','region'])[column].rank(method='min',ascending=False)
                df_aux[column_new_region_rank]=df_aux.groupby(['Date','region'])[column_new].rank(method='min',ascending=False)

            df_aux = df_aux.loc[df_aux['Date']==max(df_aux['Date'])]
            df_aux.Date = df_aux.Date.transform(lambda x:x.strftime("%B %d{}, %Y".format(ordinal(x.day))))

            status_report = df_aux.copy()

            print("Status_report table generated succesfully!")
            countries_list = status_report['Country/Region'].unique()

            if update:
                print('updating all entries in models.StatusReport')

                for item in countries_list:
                    info = status_report.loc[status_report['Country/Region']==item]
                    country = StatusReport.objects.get(country__name=item)

                    country.date=info.Date.values[0]
                    country.confirmed=int(info.Confirmed.values[0])
                    country.confirmed_new=int(info.Confirmed_new_cases.values[0])
                    country.confirmed_pct_change=float(info['Confirmed_daily_%inc_by_country'].values[0])
                    country.confirmed_rank_region=int(info.Confirmed_rank_in_region.values[0])
                    country.confirmed_rank_world=int(info.Confirmed_rank_in_world.values[0])
                    country.confirmed_new_rank_region=int(info.Confirmed_new_cases_rank_in_region.values[0])
                    country.confirmed_new_rank_world=int(info.Confirmed_new_cases_rank_in_world.values[0])
                    country.deaths=int(info.Deaths.values[0])
                    country.deaths_new=int(info.Deaths_new_cases.values[0])
                    country.deaths_pct_change=float(info['Deaths_daily_%inc_by_country'].values[0])
                    country.deaths_rank_region=int(info.Deaths_rank_in_region.values[0])
                    country.deaths_rank_world=int(info.Deaths_rank_in_world.values[0])
                    country.deaths_new_rank_region=int(info.Deaths_new_cases_rank_in_region.values[0])
                    country.deaths_new_rank_world=int(info.Deaths_new_cases_rank_in_world.values[0])
                    country.recovered=int(info.Recovered.values[0])
                    country.recovered_new=int(info.Recovered_new_cases.values[0])
                    country.recovered_pct_change=float(info['Recovered_daily_%inc_by_country'].values[0])
                    country.recovered_rank_region=int(info.Recovered_rank_in_region.values[0])
                    country.recovered_rank_world=int(info.Recovered_rank_in_world.values[0])
                    country.recovered_new_rank_region=int(info.Recovered_new_cases_rank_in_region.values[0])
                    country.recovered_new_rank_world=int(info.Recovered_new_cases_rank_in_world.values[0])
                    country.active=int(info.Active.values[0])
                    country.active_new=int(info.Active_new_cases.values[0])
                    country.active_pct_change=float(info['Active_daily_%inc_by_country'].values[0])
                    country.active_rank_region=int(info.Active_rank_in_region.values[0])
                    country.active_rank_world=int(info.Active_rank_in_world.values[0])
                    country.active_new_rank_region=int(info.Active_new_cases_rank_in_region.values[0])
                    country.active_new_rank_world=int(info.Active_new_cases_rank_in_world.values[0])

                    country.save()
                    print('{} updated in models.StatusReport'.format(item))
            else:
                db_del(StatusReport,confirm_before=confirm_value)

                print('Inserting all countries in the list to models.StatusReport')

                for item in countries_list:
                    country = Country.objects.filter(name=item)
                    if country.exists():
                        info = status_report.loc[status_report['Country/Region']==item]

                        entry = StatusReport.objects.get_or_create(country=country[0],
                                                                   date=info.Date.values[0],
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

        print('Script executed succesfully!')
    except:
        print('Something went wrong! The script was not executed')
    finally:
        print('End of execution of the populate_StatusReport.py script')


if __name__ == '__main__':
    main()
