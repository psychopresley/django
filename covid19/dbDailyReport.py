import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE','covid19.settings')
django.setup()

import numpy as np
from pandas import read_json, read_csv
from datetime import date, timedelta
from time import ctime, time
from report.functions import *
from report.models import Country, ISOCodeData, UNData, ConfigReport, DailyReport

def main():
    try:
        if dbconfig.task == 0:
            db_del(DailyReport,confirm_before=dbconfig.confirm_delete)
        else:
            countries_table = read_csv(dbconfig.aux_file_one,index_col='Country')

            # reading region dictionary:
            region_dict = countries_table['Region'].to_dict()

            print("Reading data file")
            df = read_json(dbconfig.base_file)

            print("Generating daily report table")
            df_aux = df.copy()[['Country/Region','Date']]

            df_aux['region'] = df_aux['Country/Region'].transform(lambda x: region_dict[x] if x in region_dict.keys() else x)

            column_names = ['Confirmed','Deaths','Active']
            for column in column_names:
                column_new = column + '_new_cases'

                df_aux[column] = df[column].transform(lambda x:max(x,0))
                df_aux[column_new] = df[column_new].transform(lambda x:max(x,0))

                df_aux[column_new+'_short_avg'] = df_aux.groupby('Country/Region')[column_new].rolling(window=3,min_periods=1).mean().values
                df_aux[column_new+'_medium_avg'] = df_aux.groupby('Country/Region')[column_new].rolling(window=7,min_periods=1).mean().values
                df_aux[column_new+'_long_avg'] = df_aux.groupby('Country/Region')[column_new].rolling(window=14,min_periods=1).mean().values


            # Columns calculated specificly for Status Report model db:
            df_aux['active_pct'] = (df_aux['Active'] / df_aux['Confirmed']).replace(np.nan,0)
            df_aux['mortality'] = (df_aux['Deaths'] / df_aux['Confirmed']).replace(np.nan,0)
            df_aux.Date = df_aux.Date.transform(lambda x:date(x.year, x.month, x.day))

            daily_report = df_aux.copy()

            print("Daily_report table generated succesfully!")
            countries_list = daily_report['Country/Region'].unique()

            if dbconfig.task == 1:
                db_most_recent_date = DailyReport.objects.all().order_by('-date')[0].date
                file_most_recent_date = daily_report.loc[daily_report['Date']==max(daily_report['Date'])]['Date'].unique()

                if db_most_recent_date >= file_most_recent_date:
                    print('database already up-to-date')
                    pass
                else:
                    daily_report = daily_report.loc[daily_report['Date'] > db_most_recent_date]
                    print('inserting new entries into models.DailyReport')

                for item in countries_list:
                    country = Country.objects.filter(name=item)

                    if country.exists():
                        info_country = daily_report.loc[daily_report['Country/Region']==item]
                        pop = population(item)

                        for item_date in info_country['Date'].unique():
                            info = info_country.loc[info_country['Date']==item_date]

                            entry = DailyReport.objects.get_or_create(country=country[0],
                                                                      date=info.Date.values[0],
                                                                      confirmed=int(info.Confirmed.values[0]),
                                                                      confirmed_new=int(info.Confirmed_new_cases.values[0]),
                                                                      confirmed_new_short_avg=int(info.Confirmed_new_cases_short_avg.values[0]),
                                                                      confirmed_new_medium_avg=int(info.Confirmed_new_cases_medium_avg.values[0]),
                                                                      confirmed_new_long_avg=int(info.Confirmed_new_cases_long_avg.values[0]),
                                                                      confirmed_by_hundreds=int(info.Confirmed.values[0]*0.1/pop),
                                                                      confirmed_new_by_hundreds=int(info.Confirmed_new_cases.values[0]*0.1/pop),
                                                                      deaths=int(info.Deaths.values[0]),
                                                                      deaths_new=int(info.Deaths_new_cases.values[0]),
                                                                      deaths_new_short_avg=int(info.Deaths_new_cases_short_avg.values[0]),
                                                                      deaths_new_medium_avg=int(info.Deaths_new_cases_medium_avg.values[0]),
                                                                      deaths_new_long_avg=int(info.Deaths_new_cases_long_avg.values[0]),
                                                                      deaths_by_hundreds=int(info.Deaths.values[0]*0.1/pop),
                                                                      deaths_new_by_hundreds=int(info.Deaths_new_cases.values[0]*0.1/pop),
                                                                      active=int(info.Active.values[0]),
                                                                      active_new=int(info.Active_new_cases.values[0]),
                                                                      active_pct=float(info.active_pct.values[0]),
                                                                      active_by_hundreds=int(info.Active.values[0]*0.1/pop),
                                                                      mortality=float(info.mortality.values[0]),)[0]

                            entry.save()
                        print('{} inserted into models.DailyReport'.format(item))
                    else:
                        print(item + ' is not on DailyReport.models')
            else:
                db_del(DailyReport,confirm_before=dbconfig.confirm_delete)

                print('Inserting all countries in the list to models.DailyReport')

                for item in countries_list:
                    country = Country.objects.filter(name=item)

                    if country.exists():
                        info_country = daily_report.loc[daily_report['Country/Region']==item]
                        pop = population(item)

                        for item_date in info_country['Date'].unique():
                            info = info_country.loc[info_country['Date']==item_date]

                            entry = DailyReport.objects.get_or_create(country=country[0],
                                                                      date=info.Date.values[0],
                                                                      confirmed=int(info.Confirmed.values[0]),
                                                                      confirmed_new=int(info.Confirmed_new_cases.values[0]),
                                                                      confirmed_new_short_avg=int(info.Confirmed_new_cases_short_avg.values[0]),
                                                                      confirmed_new_medium_avg=int(info.Confirmed_new_cases_medium_avg.values[0]),
                                                                      confirmed_new_long_avg=int(info.Confirmed_new_cases_long_avg.values[0]),
                                                                      confirmed_by_hundreds=int(info.Confirmed.values[0]*0.1/pop),
                                                                      confirmed_new_by_hundreds=int(info.Confirmed_new_cases.values[0]*0.1/pop),
                                                                      deaths=int(info.Deaths.values[0]),
                                                                      deaths_new=int(info.Deaths_new_cases.values[0]),
                                                                      deaths_new_short_avg=int(info.Deaths_new_cases_short_avg.values[0]),
                                                                      deaths_new_medium_avg=int(info.Deaths_new_cases_medium_avg.values[0]),
                                                                      deaths_new_long_avg=int(info.Deaths_new_cases_long_avg.values[0]),
                                                                      deaths_by_hundreds=int(info.Deaths.values[0]*0.1/pop),
                                                                      deaths_new_by_hundreds=int(info.Deaths_new_cases.values[0]*0.1/pop),
                                                                      active=int(info.Active.values[0]),
                                                                      active_new=int(info.Active_new_cases.values[0]),
                                                                      active_pct=float(info.active_pct.values[0]),
                                                                      active_by_hundreds=int(info.Active.values[0]*0.1/pop),
                                                                      mortality=float(info.mortality.values[0]),)[0]

                            entry.save()
                        print('{} inserted into models.DailyReport'.format(item))
                    else:
                        print(item + ' is not on DailyReport.models')

        dbconfig.log_status=1
        dbconfig.date=current_date
    except:
        dbconfig.log_status=2
    finally:
        print('End of {} script'.format(os.path.basename(__file__)))


if __name__ == '__main__':

    script_start_time = time()

    # Retieving configuration info:
    dbconfig = ConfigReport.objects.get(var_name__contains='DailyReport')

    current_date = ctime(os.path.getmtime(dbconfig.base_file))
    if current_date == dbconfig.date and dbconfig.auto_exec:
        dbconfig.log_status=0
    else:
        main()

    dbconfig.time_exec=round(time()-script_start_time,2)
    dbconfig.save()
