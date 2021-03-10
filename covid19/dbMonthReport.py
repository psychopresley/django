import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE','covid19.settings')
django.setup()

from pandas import read_json, read_csv
from datetime import date
from numpy import inf, nan
from time import ctime
from calendar import monthrange
from report.models import Country, MonthReport

def main():
    def db_del(database,confirm_before=True):
        # This function delete all entries in "database" model

        flag = True

        if confirm_before:
            confirm_delete = input('This will erase all entries in models.MonthReport. Press "n" if you wish to skip delete or any other key to continue: ')

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

    try:
        # In the config.csv file, on 'countryinfo_file' row of columns 'var':
        #  - aux1: Set 0, for delete all entries in database or 1 for add/update entries;
        #  - aux2: Set 0, for reload database from 'country_report.json' file or 1 for update existing entries;
        #  - aux3: Set 1, for confirmation need in case aux1 is set to 0;

        log_dbMonthReport=[]
        log_dbMonthReport.append('\n----------dbMonthReport.py SCRIPT EXECUTION REPORT-----------\n')
        log_dbMonthReport.append('\n'+ 'Local time: ' + ctime() + '\n\n')

        task = config.loc['month_report'].aux1
        update = config.loc['month_report'].aux2
        confirm_value=config.loc['month_report'].aux3

        if not task:
            db_del(MonthReport,confirm_before=confirm_value)
        else:
            country_report = os.path.join(config.loc['month_report'].file_path,
                                              config.loc['month_report'].file_name)

            country_table_file = os.path.join(config.loc['countryinfo_file'].file_path,
                                              config.loc['countryinfo_file'].file_name)

            label_map_file = os.path.join(config.loc['labelmap_file'].file_path,
                                              config.loc['labelmap_file'].file_name)

            countries_table = read_csv(country_table_file,index_col='Country')

            # reading region dictionary:
            region_dict = countries_table['Region'].to_dict()
            label_dict = read_csv(label_map_file,header=None,index_col=0).to_dict()[1]

            print("Reading 'country_report.json' file")
            df = read_json(country_report)

            print("Creating month report table")
            df_aux = df.copy()[['Country/Region','Date']]

            df_aux['Country/Region'] = df_aux['Country/Region'].transform(lambda x: label_dict[x] if x in label_dict.keys() else x)
            df_aux['month'] = df_aux['Date'].transform(lambda x:date(x.year, x.month, x.day).strftime('%Y-%m'))

            column_names = ['Confirmed','Deaths']
            for column in column_names:
                df_aux[column] = df[column + '_new_cases']

            df_aux = df_aux.groupby(['Country/Region','month']).sum().reset_index()
            for column in column_names:
                df_aux[column] = df_aux[column].transform(lambda x:max(x,0))

            df_aux['region'] = df_aux['Country/Region'].transform(lambda x: region_dict[x] if x in region_dict.keys() else x)

            for column in column_names:
                df_aux[column + '_pct_change'] = df_aux.groupby('Country/Region')[column].pct_change()*100
                df_aux[column + '_pct_change'].replace(to_replace=[-inf, inf],value=nan,inplace=True)
                df_aux[column + '_pct_change'].fillna(value=0,inplace=True)

                df_aux[column + '_rank_world'] = df_aux.groupby('month')[column].rank(method='min',ascending=False)
                df_aux[column + '_rank_region'] = df_aux.groupby(['month','region'])[column].rank(method='min',ascending=False)

            df_aux['days_in_month'] = df_aux['month'].transform(lambda x:monthrange(int(x[:4]),int(x[-2:]))[1])
            df_aux['last_update'] = df['Date'].max()
            df_aux['last_update'] = df_aux['last_update'].transform(lambda x:date(x.year,x.month,x.day))

            month_report = df_aux.copy()
            print("month_report table generated succesfully!")

            countries_list = month_report['Country/Region'].unique()

            if update:
                print('updating all entries in models.MonthReport')

                for item in countries_list:
                    df_info = month_report.loc[month_report['Country/Region']==item]
                    country = MonthReport.objects.filter(country=item)

                    for obj in country:
                        param = df_info.loc[df_info.month == obj.__dict__['month']]

                        obj.month=param.month.values[0]
                        obj.confirmed=int(param.Confirmed.values[0])
                        obj.confirmed_pct_change=float(param.Confirmed_pct_change.values[0])
                        obj.confirmed_rank_region=int(param.Confirmed_rank_region.values[0])
                        obj.confirmed_rank_world=int(param.Confirmed_rank_world.values[0])
                        obj.deaths=int(param.Deaths.values[0])
                        obj.deaths_pct_change=float(param.Deaths_pct_change.values[0])
                        obj.deaths_rank_region=int(param.Deaths_rank_region.values[0])
                        obj.deaths_rank_world=int(param.Deaths_rank_world.values[0])
                        obj.days_in_month=int(param.days_in_month.values[0])
                        obj.last_update=param.last_update.values[0]

                        obj.save()
                    print('{} updated in models.MonthReport'.format(item))
                # log_dbMonthReport.append('\n models.MonthReport updated succesfully \n')
            else:
                db_del(MonthReport,confirm_before=confirm_value)

                print('Inserting all countries in the list to models.MonthReport')

                for item in countries_list:
                    country = Country.objects.filter(name=item)

                    if country.exists():
                        df_info = month_report.loc[month_report['Country/Region']==item]
                        for i in df_info.index:
                            param = df_info.loc[i]
                            entry = MonthReport.objects.get_or_create(country=country[0],
                                                                      month=param.month,
                                                                      confirmed=param.Confirmed,
                                                                      confirmed_pct_change=param.Confirmed_pct_change,
                                                                      confirmed_rank_region=int(param.Confirmed_rank_region),
                                                                      confirmed_rank_world=int(param.Confirmed_rank_world),
                                                                      deaths=param.Deaths,
                                                                      deaths_pct_change=param.Deaths_pct_change,
                                                                      deaths_rank_region=int(param.Deaths_rank_region),
                                                                      deaths_rank_world=int(param.Deaths_rank_world),
                                                                      days_in_month=param.days_in_month,
                                                                      last_update=param.last_update)[0]

                            entry.save()
                        print('{} inserted into models.MonthReport'.format(item))
                    else:
                        print(item + ' is not on Country.models')

        message = 'Script executed succesfully!'
        print(message)
        log_dbMonthReport.append('\n Most recent date on report: {} \n'.format(MonthReport.objects.order_by('-month')[0].month))
        log_dbMonthReport.append('\n {} \n'.format(message))
    except:
        message = 'Something went wrong! The script was not executed'
        print(message)
        log_dbMonthReport.append('\n {} \n'.format(message))
    finally:
        message = 'End of execution of the dbMonthReport.py script'
        print(message)
        log_dbMonthReport.append('\n {} \n'.format(message))

        log_dir = r'C:\Users\user\Documents\GitHub\django\covid19\static\report\log'
        os.chdir(log_dir)

        log = open('log_dbMonthReport.txt','w')
        log.writelines(log_dbMonthReport)
        log.close()



if __name__ == '__main__':
    config_filepath = r"C:\Users\user\Documents\GitHub\django\covid19\static\report\config"

    if 'config.csv' in os.listdir(config_filepath):
        print('Reading configuration file')
        config = read_csv(os.path.join(config_filepath,'config.csv'),index_col='var').fillna('-')
    else:
        raise FileNotFoundError('No configuration file "config.csv" found.')

    country_report = os.path.join(config.loc['month_report'].file_path,
                                  config.loc['month_report'].file_name)

    last_modified = config.loc['month_report'].aux4
    current_date = ctime(os.path.getmtime(country_report))

    if current_date == last_modified and False:
        log_dbMonthReport=[]
        log_dbMonthReport.append('\n----------dbMonthReport.py SCRIPT EXECUTION REPORT-----------\n')
        log_dbMonthReport.append('\n'+ 'Local time: ' + ctime() + '\n\n')
        log_dbMonthReport.append('\n --> current file has not been modified. Nothing to do here.')

        log_dir = r'C:\Users\user\Documents\GitHub\django\covid19\static\report\log'
        os.chdir(log_dir)

        log = open('log_dbMonthReport.txt','w')
        log.writelines(log_dbMonthReport)
        log.close()

        print('No necessary actions for the current file')
        pass
    else:
        main()

        os.chdir(config_filepath)
        config.loc['month_report','aux4'] = current_date
        config.to_csv('config.csv')
