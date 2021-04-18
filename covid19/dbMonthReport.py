import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE','covid19.settings')
django.setup()

from pandas import read_json, read_csv
from datetime import date
from numpy import inf, nan
from time import ctime, time
from calendar import monthrange
from report.models import Country, MonthReport, ConfigReport

# Retieving configuration info:
dbconfig = ConfigReport.objects.get(var_name__contains='MonthReport')


def report(df,region_dict,label_dict):
    '''
    This function will manipulate the country_report.json file in order to obtain
    the dataframe with the columns representing the models.MonthReport attributes

    region_dict and label_dict are dictionaries necessary for data transformation
    '''

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

    return df_aux


def update_db(df,modeldb):
    # Updating selected objects attributes:
    for obj in modeldb:
        param = df.loc[df['Country/Region'] == obj.country.name]

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
        print('{} updated in database'.format(obj.country.name))


def insert_db(df,countries_list):
    print('Inserting all countries in the list to models.MonthReport')

    for item in countries_list:
        country = Country.objects.filter(name=item)

        if country.exists():
            df_info = df.loc[df['Country/Region']==item]
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
        if  dbconfig.task == 0: # This will delete the entire MonthReport database
            db_del(MonthReport,confirm_before=dbconfig.confirm_delete)

        else: # This will update or create the MonthReport database

            # ---------------------------
            # Reading Configuration files
            countries_table = read_csv(dbconfig.aux_file_one,index_col='Country')

            #--------------------- ---------------------------
            # reading region dictionary and labels dictionary:
            region_dict = countries_table['Region'].to_dict()
            label_dict = read_csv(dbconfig.aux_file_two,header=None,index_col=0).to_dict()[1]

            # -----------------------------------
            # Creating the month_report dataframe
            print("Reading data file")
            df = read_json(dbconfig.base_file)

            print("Creating month report table")

            month_report = report(df,region_dict,label_dict)
            countries_list = month_report['Country/Region'].unique()

            print("month_report table generated succesfully!")

            # =================================================================
            # Now, let's compare the latest month in table with the latest month
            # in database. If they are the same, update is enabled. Otherwise, a
            # database insert query is called:

            db_last_month = MonthReport.objects.order_by('-month')[0].month

            x = month_report.last_update.max()
            report_last_month = date(x.year, x.month, x.day).strftime('%Y-%m')

            if db_last_month == report_last_month:
                flag_update = 'update'
            else:
                year_in_report = int(report_last_month[:4])
                year_in_db = int(db_last_month[:4])

                month_in_report = int(report_last_month[-2:])
                month_in_db = int(db_last_month[-2:])

                if year_in_report < year_in_db:
                    flag_update = 'ahead'
                else:
                    if month_in_report > month_in_db:
                        flag_update = 'insert'
                    else:
                        flag_update = 'ahead'

            # =================================================================

            if dbconfig.task == 1:
                print('updating all entries in models.MonthReport')

                # Once update is enabled, the month_report dataframe will be filtered
                # to the last 'year-month' and the objects in database will be filtered
                # to those in the same year-month in order to save memory resources:
                if flag_update == 'update':
                    df = month_report.loc[month_report['month']==db_last_month]
                    modeldb = MonthReport.objects.filter(month=db_last_month)

                    update_db(df,modeldb)
                elif flag_update == 'insert':
                    # In case there's a difference between months or years between
                    # the report and the database, first we update the last month
                    # in the database and then we insert the other months new objects

                    # 1 - Update last month in database:
                    df = month_report.loc[month_report['month']==db_last_month]
                    modeldb = MonthReport.objects.filter(month=db_last_month)

                    update_db(df,modeldb)

                    # 2 - Insert new month(s) in database:
                    df = month_report.loc[month_report['month'] > db_last_month]
                    insert_db(df,countries_list)
                else:
                    pass
            else:
                db_del(MonthReport,confirm_before=dbconfig.confirm_delete)
                insert_db(month_report,countries_list)

        message = 'Script executed succesfully!'
        print(message)
        dbconfig.log_status=1
    except:
        message = 'Something went wrong! The script was not executed'
        print(message)
        dbconfig.log_status=2



if __name__ == '__main__':
    script_start_time = time()
    current_date = ctime(os.path.getmtime(dbconfig.base_file))

    if current_date == dbconfig.date and dbconfig.auto_exec:
        dbconfig.log_status=0
        dbconfig.time_exec=round(time()-script_start_time,2)
        dbconfig.save()
    else:
        main()

        dbconfig.date=current_date
        dbconfig.time_exec=round(time()-script_start_time,2)
        dbconfig.save()
