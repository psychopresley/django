import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE','covid19.settings')
django.setup()

from pandas import read_csv
from time import ctime, time
from report.models import Country, ConfigReport

def db_del(database,confirm_before=True):
    # This function delete all entries in "database" model

    flag = True

    if confirm_before:
        confirm_delete = input('This will erase all entries in models.{}. Press "n" if you wish to skip delete or any other key to continue: '.format(database))

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

def main():
    try:
        if dbconfig.task == 0:
            db_del(Country,confirm_before=dbconfig.confirm_delete)
        else:
            countries_table = read_csv(dbconfig.aux_file_one)
            countries_list = countries_table['Country'].unique()

            if dbconfig.task == 1:
                print('updating all entries in models.Country')

                for item in countries_list:
                    info = countries_table.loc[countries_table['Country']==item]
                    country = Country.objects.get(name=item)

                    country.latitude = float(info.Latitude.values[0])
                    country.longitude = float(info.Longitude.values[0])
                    country.region = region=info.Region.values[0]
                    country.internet_code = info.internet_code.values[0]
                    country.map_image = info.map_image.values[0]

                    country.save()
                    print('{} updated in models.Country'.format(item))
            else:
                db_del(Country,confirm_before=dbconfig.confirm_delete)

                print('Inserting all countries in the list to models.Country')

                for item in countries_list:
                    info = countries_table.loc[countries_table['Country']==item]

                    entry = Country.objects.get_or_create(name=item,
                                                          latitude=info.Latitude.values[0],
                                                          longitude=info.Longitude.values[0],
                                                          region=info.Region.values[0],
                                                          internet_code=info.internet_code.values[0],
                                                          map_image=info.map_image.values[0])[0]
                    entry.save()

                    print(item + ' inserted into models.Country')

        dbconfig.log_status=1
    except:
        dbconfig.log_status=2
    finally:
        print('End of {} script'.format(os.path.basename(__file__)))


if __name__ == '__main__':

    script_start_time = time()

    # Retieving configuration info:
    dbconfig = ConfigReport.objects.get(var_name='dbconfig_Country')

    main()

    dbconfig.time_exec=round(time()-script_start_time,2)
    dbconfig.save()
