import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE','covid19.settings')
django.setup()

import numpy as np
from pandas import read_json, read_csv
from datetime import date, timedelta
from time import ctime
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

    # creating quartiles map function:
    def quart_func(x,q,case):
        if x < q[1]:
            return '1st (very low {})'.format(case.lower())
        elif q[1] <= x < q[2]:
            return '2nd (medium-low {})'.format(case.lower())
        elif q[2] <= x < q[3]:
            return '3rd (medium-high {})'.format(case.lower())
        else:
            return '4th (very high {})'.format(case.lower())

    # creating quartiles map function:
    def quantiles_pos(mortality, model_coef):
        return ([mortality**4,mortality**3,mortality**2,mortality,1]*model_coef).item()

    # creating quartiles map function:
    def quantiles_model(quantiles):
        regressors = []
        y=[]
        for k,v in quantiles.items():
            regressors.append([v**4,v**3,v**2,v,1])
            y.append([k])

        regressors = np.matrix(regressors)
        model_coef = np.linalg.inv(regressors)*np.array(y)

        return model_coef


    try:
        # In the config.csv file, on 'countryinfo_file' row of columns 'var':
        #  - aux1: Set 0, for delete all entries in database or 1 for add/update entries;
        #  - aux2: Set 0, for reload database from 'country_report.json' file or 1 for update existing entries;
        #  - aux3: Set 1, for confirmation need in case aux1 is set to 0;

        log_dbStatusReport=[]
        log_dbStatusReport.append('\n----------dbStatusReport.py SCRIPT EXECUTION REPORT-----------\n')
        log_dbStatusReport.append('\n'+ 'Local time: ' + ctime() + '\n\n')

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

            # Columns calculated specificly for Status Report model db:
            df_aux['active_pct'] = df_aux['Active'] / df_aux['Confirmed']
            df_aux['mortality'] = df_aux['Deaths'] / df_aux['Confirmed']
            df_aux['mortality_rank_region'] = df_aux.groupby(['Date','region'])['mortality'].rank(method='min',ascending=False)
            df_aux['mortality_rank_world'] = df_aux.groupby('Date')['mortality'].rank(method='min',ascending=False)

            # Filtering by the latest date:
            previous_report = df_aux.loc[df_aux['Date']==(max(df_aux['Date'])-timedelta(days=1))]
            df_aux = df_aux.loc[df_aux['Date']==max(df_aux['Date'])]
            df_aux.Date = df_aux.Date.transform(lambda x:date(x.year, x.month, x.day))


            # Defining quartile intervals for the mortality:
            quantile=df_aux['mortality'].quantile(q=[0,0.1,0.5,0.9,1])
            df_aux['mortality_quartile']=df_aux['mortality'].apply(lambda x:quart_func(x,quantile.values,'mortality'))

            model_coef = quantiles_model(quantile.to_dict())
            print(quantile.to_dict(),model_coef)
            df_aux['mortality_quartile_position']=df_aux['mortality'].apply(lambda x:quantiles_pos(x,model_coef))

            status_report = df_aux.copy()

            print("Status_report table generated succesfully!")
            countries_list = status_report['Country/Region'].unique()

            if update:
                print('updating all entries in models.StatusReport')

                for item in countries_list:
                    info = status_report.loc[status_report['Country/Region']==item]
                    previous_info = previous_report.loc[previous_report['Country/Region']==item]
                    country = StatusReport.objects.get(country__name=item)

                    print([info.mortality.values[0],info.mortality_quartile_position.values[0]])
                    if previous_info.Confirmed_new_cases.values[0] == 0:
                        confirmed_new_pct_change = 0
                    else:
                        confirmed_new_pct_change = (info.Confirmed_new_cases.values[0] - previous_info.Confirmed_new_cases.values[0])*100/previous_info.Confirmed_new_cases.values[0]

                    if previous_info.Deaths_new_cases.values[0] == 0:
                        deaths_new_pct_change = 0
                    else:
                        deaths_new_pct_change = (info.Deaths_new_cases.values[0] - previous_info.Deaths_new_cases.values[0])*100/previous_info.Deaths_new_cases.values[0]

                    country.date=info.Date.values[0]
                    country.db_update=date.today()
                    country.confirmed=int(info.Confirmed.values[0])
                    country.confirmed_new=int(info.Confirmed_new_cases.values[0])
                    country.confirmed_new_pct_change=float(confirmed_new_pct_change)
                    country.confirmed_pct_change=float(info['Confirmed_daily_%inc_by_country'].values[0])
                    country.confirmed_rank_region=int(info.Confirmed_rank_in_region.values[0])
                    country.confirmed_rank_world=int(info.Confirmed_rank_in_world.values[0])
                    country.confirmed_new_rank_region=int(info.Confirmed_new_cases_rank_in_region.values[0])
                    country.confirmed_new_rank_world=int(info.Confirmed_new_cases_rank_in_world.values[0])
                    country.deaths=int(info.Deaths.values[0])
                    country.deaths_new=int(info.Deaths_new_cases.values[0])
                    country.deaths_new_pct_change=float(deaths_new_pct_change)
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
                    country.active_pct=float(info.active_pct.values[0])
                    country.active_pct_change=float(info['Active_daily_%inc_by_country'].values[0])
                    country.active_rank_region=int(info.Active_rank_in_region.values[0])
                    country.active_rank_world=int(info.Active_rank_in_world.values[0])
                    country.active_new_rank_region=int(info.Active_new_cases_rank_in_region.values[0])
                    country.active_new_rank_world=int(info.Active_new_cases_rank_in_world.values[0])
                    country.mortality=float(info.mortality.values[0])
                    country.mortality_quartile=info.mortality_quartile.values[0]
                    country.mortality_quartile_position=info.mortality_quartile_position.values[0]
                    country.mortality_rank_region=int(info.mortality_rank_region.values[0])
                    country.mortality_rank_world=int(info.mortality_rank_world.values[0])

                    country.save()
                    print('{} updated in models.StatusReport'.format(item))
                log_dbStatusReport.append('\n models.StatusReport updated succesfully \n')
            else:
                db_del(StatusReport,confirm_before=confirm_value)

                print('Inserting all countries in the list to models.StatusReport')

                for item in countries_list:
                    country = Country.objects.filter(name=item)

                    if country.exists():
                        info = status_report.loc[status_report['Country/Region']==item]
                        previous_info = previous_report.loc[previous_report['Country/Region']==item]

                        if previous_info.Confirmed_new_cases.values[0] == 0:
                            confirmed_new_pct_change = 0
                        else:
                            confirmed_new_pct_change = (info.Confirmed_new_cases.values[0] - previous_info.Confirmed_new_cases.values[0])*100/previous_info.Confirmed_new_cases.values[0]

                        if previous_info.Deaths_new_cases.values[0] == 0:
                            deaths_new_pct_change = 0
                        else:
                            deaths_new_pct_change = (info.Deaths_new_cases.values[0] - previous_info.Deaths_new_cases.values[0])*100/previous_info.Deaths_new_cases.values[0]


                        entry = StatusReport.objects.get_or_create(country=country[0],
                                                                   date=info.Date.values[0],
                                                                   db_update=date.today(),
                                                                   confirmed=int(info.Confirmed.values[0]),
                                                                   confirmed_new=int(info.Confirmed_new_cases.values[0]),
                                                                   confirmed_new_pct_change=float(confirmed_new_pct_change),
                                                                   confirmed_pct_change=float(info['Confirmed_daily_%inc_by_country'].values[0]),
                                                                   confirmed_rank_region=int(info.Confirmed_rank_in_region.values[0]),
                                                                   confirmed_rank_world=int(info.Confirmed_rank_in_world.values[0]),
                                                                   confirmed_new_rank_region=int(info.Confirmed_new_cases_rank_in_region.values[0]),
                                                                   confirmed_new_rank_world=int(info.Confirmed_new_cases_rank_in_world.values[0]),
                                                                   deaths=int(info.Deaths.values[0]),
                                                                   deaths_new=int(info.Deaths_new_cases.values[0]),
                                                                   deaths_new_pct_change=float(deaths_new_pct_change),
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
                                                                   active_pct=float(info.active_pct.values[0]),
                                                                   active_pct_change=float(info['Active_daily_%inc_by_country'].values[0]),
                                                                   active_rank_region=int(info.Active_rank_in_region.values[0]),
                                                                   active_rank_world=int(info.Active_rank_in_world.values[0]),
                                                                   active_new_rank_region=int(info.Active_new_cases_rank_in_region.values[0]),
                                                                   active_new_rank_world=int(info.Active_new_cases_rank_in_world.values[0]),
                                                                   mortality_rank_region=int(info.mortality_rank_region.values[0]),
                                                                   mortality_rank_world=int(info.mortality_rank_world.values[0]),
                                                                   mortality=float(info.mortality.values[0]),
                                                                   mortality_quartile=info.mortality_quartile.values[0],
                                                                   mortality_quartile_position=info.mortality_quartile_position.values[0],)[0]

                        entry.save()
                        print('{} inserted into models.StatusReport'.format(item))
                    else:
                        print(item + ' is not on StatusReport.models')

        message = 'Script executed succesfully!'
        print(message)
        log_dbStatusReport.append('\n Most recent date on report: {} \n'.format(StatusReport.objects.order_by('-date')[0].date))
        log_dbStatusReport.append('\n {} \n'.format(message))
    except:
        message = 'Something went wrong! The script was not executed'
        print(message)
        log_dbStatusReport.append('\n {} \n'.format(message))
    finally:
        message = 'End of execution of the populate_StatusReport.py script'
        print(message)
        log_dbStatusReport.append('\n {} \n'.format(message))

        log_dir = r'C:\Users\user\Documents\GitHub\django\covid19\static\report\log'
        os.chdir(log_dir)

        log = open('log_dbStatusReport.txt','w')
        log.writelines(log_dbStatusReport)
        log.close()



if __name__ == '__main__':
    config_filepath = r"C:\Users\user\Documents\GitHub\django\covid19\static\report\config"

    if 'config.csv' in os.listdir(config_filepath):
        print('Reading configuration file')
        config = read_csv(os.path.join(config_filepath,'config.csv'),index_col='var').fillna('-')
    else:
        raise FileNotFoundError('No configuration file "config.csv" found.')

    country_report = os.path.join(config.loc['status_report'].file_path,
                                  config.loc['status_report'].file_name)

    last_modified = config.loc['status_report'].aux4
    current_date = ctime(os.path.getmtime(country_report))

    if current_date == last_modified and False:
        log_dbStatusReport=[]
        log_dbStatusReport.append('\n----------dbStatusReport.py SCRIPT EXECUTION REPORT-----------\n')
        log_dbStatusReport.append('\n'+ 'Local time: ' + ctime() + '\n\n')
        log_dbStatusReport.append('\n --> current file has not been modified. Nothing to do here.')

        log_dir = r'C:\Users\user\Documents\GitHub\django\covid19\static\report\log'
        os.chdir(log_dir)

        log = open('log_dbStatusReport.txt','w')
        log.writelines(log_dbStatusReport)
        log.close()

        print('No necessary actions for the current file')
        pass
    else:
        main()

        os.chdir(config_filepath)
        config.loc['status_report','aux4'] = current_date
        config.to_csv('config.csv')
