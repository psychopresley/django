import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE','covid19.settings')
django.setup()

from pandas import read_json, read_csv
from datetime import date
from numpy import inf, nan
from time import ctime, time
from report.models import Country, WeekReport, ConfigReport

# Retieving configuration info:
dbconfig = ConfigReport.objects.get(var_name__contains='WeekReport')


def report(df,region_dict,label_dict):
    '''
    This function will manipulate the country_report.json file in order to obtain
    the dataframe with the columns representing the models.WeekReport attributes

    region_dict and label_dict are dictionaries necessary for data transformation
    '''

    df_aux = df.copy()[['Country/Region','Date']]
    df_aux['Country/Region'] = df_aux['Country/Region'].transform(lambda x: label_dict[x] if x in label_dict.keys() else x)
    df_aux['week'] = df_aux['Date'].transform(lambda x:date(x.year, x.month, x.day).strftime('%Y-%U'))

    column_names = ['Confirmed','Deaths']
    for column in column_names:
        df_aux[column] = df[column + '_new_cases']

    df_aux = df_aux.groupby(['Country/Region','week']).sum().reset_index()
    for column in column_names:
        df_aux[column] = df_aux[column].transform(lambda x:max(x,0))

    df_aux['region'] = df_aux['Country/Region'].transform(lambda x: region_dict[x] if x in region_dict.keys() else x)

    for column in column_names:
        df_aux[column + '_pct_change'] = df_aux.groupby('Country/Region')[column].pct_change()*100
        df_aux[column + '_pct_change'].replace(to_replace=[-inf, inf],value=nan,inplace=True)
        df_aux[column + '_pct_change'].fillna(value=0,inplace=True)

        df_aux[column + '_rank_world'] = df_aux.groupby('week')[column].rank(method='min',ascending=False)
        df_aux[column + '_rank_region'] = df_aux.groupby(['week','region'])[column].rank(method='min',ascending=False)

    df_aux['last_update'] = df['Date'].max()
    df_aux['last_update'] = df_aux['last_update'].transform(lambda x:date(x.year,x.month,x.day))

    return df_aux


def update_db(df,modeldb):
    # Updating selected objects attributes:
    for obj in modeldb:
        param = df.loc[df['Country/Region'] == obj.country.name]

        obj.week=param.week.values[0]
        obj.confirmed=int(param.Confirmed.values[0])
        obj.confirmed_pct_change=float(param.Confirmed_pct_change.values[0])
        obj.confirmed_rank_region=int(param.Confirmed_rank_region.values[0])
        obj.confirmed_rank_world=int(param.Confirmed_rank_world.values[0])
        obj.deaths=int(param.Deaths.values[0])
        obj.deaths_pct_change=float(param.Deaths_pct_change.values[0])
        obj.deaths_rank_region=int(param.Deaths_rank_region.values[0])
        obj.deaths_rank_world=int(param.Deaths_rank_world.values[0])
        obj.last_update=param.last_update.values[0]

        obj.save()
        print('{} updated in database'.format(obj.country.name))


def insert_db(df,countries_list):
    print('Inserting all countries in the list to models.WeekReport')

    for item in countries_list:
        country = Country.objects.filter(name=item)

        if country.exists():
            df_info = df.loc[df['Country/Region']==item]
            for i in df_info.index:
                param = df_info.loc[i]
                entry = WeekReport.objects.get_or_create(country=country[0],
                                                          week=param.week,
                                                          confirmed=param.Confirmed,
                                                          confirmed_pct_change=param.Confirmed_pct_change,
                                                          confirmed_rank_region=int(param.Confirmed_rank_region),
                                                          confirmed_rank_world=int(param.Confirmed_rank_world),
                                                          deaths=param.Deaths,
                                                          deaths_pct_change=param.Deaths_pct_change,
                                                          deaths_rank_region=int(param.Deaths_rank_region),
                                                          deaths_rank_world=int(param.Deaths_rank_world),
                                                          last_update=param.last_update)[0]

                entry.save()
            print('{} inserted into models.WeekReport'.format(item))
        else:
            print(item + ' is not on Country.models')


def main():
    def db_del(database,confirm_before=True):
        # This function delete all entries in "database" model

        flag = True

        if confirm_before:
            confirm_delete = input('This will erase all entries in models.WeekReport. Press "n" if you wish to skip delete or any other key to continue: ')

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
        if dbconfig.task == 0:
            db_del(WeekReport,confirm_before=dbconfig.confirm_delete)

        else: # This will update or create the WeekReport database

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

            print("Creating week report table")

            week_report = report(df,region_dict,label_dict)
            countries_list = week_report['Country/Region'].unique()

            print("week_report table generated succesfully!")

            # =================================================================

            if dbconfig.task == 1:

                # =================================================================
                # Now, let's compare the latest week in table with the latest week
                # in database. If they are the same, update is enabled. Otherwise, a
                # database insert query is called:

                db_last_week = WeekReport.objects.order_by('-week')[0].week

                x = week_report.last_update.max()
                report_last_week = date(x.year, x.month, x.day).strftime('%Y-%U')

                if db_last_week == report_last_week:
                    flag_update = 'update'
                else:
                    year_in_report = int(report_last_week[:4])
                    year_in_db = int(db_last_week[:4])

                    week_in_report = int(report_last_week[-2:])
                    week_in_db = int(db_last_week[-2:])

                    if year_in_report < year_in_db:
                        flag_update = 'ahead'
                    else:
                        if week_in_report > week_in_db:
                            flag_update = 'insert'
                        else:
                            flag_update = 'ahead'

                print('updating all entries in models.WeekReport')

                # Once update is enabled, the week_report dataframe will be filtered
                # to the last 'year-week' and the objects in database will be filtered
                # to those in the same year-week in order to save memory resources:
                if flag_update == 'update':
                    df = week_report.loc[week_report['week']==db_last_week]
                    modeldb = WeekReport.objects.filter(week=db_last_week)

                    update_db(df,modeldb)
                elif flag_update == 'insert':
                    # In case there's a difference between weeks or years between
                    # the report and the database, first we update the last week
                    # in the database and then we insert the other weeks new objects

                    # 1 - Update last week in database:
                    df = week_report.loc[week_report['week']==db_last_week]
                    modeldb = WeekReport.objects.filter(week=db_last_week)

                    update_db(df,modeldb)

                    # 2 - Insert new week(s) in database:
                    df = week_report.loc[week_report['week'] > db_last_week]
                    insert_db(df,countries_list)
                else:
                    pass
            else:
                db_del(WeekReport,confirm_before=dbconfig.confirm_delete)
                insert_db(week_report,countries_list)

        dbconfig.log_status=1
    except:
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
