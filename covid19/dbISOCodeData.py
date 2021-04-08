import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE','covid19.settings')
django.setup()

import pandas as pd
from report.models import ISOCodeData

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

        config_filepath = r"C:\Users\user\Documents\GitHub\django\covid19\static\report\config"
        file_name = 'isocode_data.csv'

        if file_name in os.listdir(config_filepath):
            print('Reading configuration file')
            df_iso = pd.read_csv(os.path.join(config_filepath,file_name),na_filter=False)
        else:
    	    raise FileNotFoundError('No configuration file {} found.'.format(file_name))

        db_del(ISOCodeData,confirm_before=False)
        print('Inserting all entries into models.ISOCodeData')

        for item in df_iso['country_iso_code'].values:
            info = df_iso.loc[df_iso['country_iso_code']==item]

            geoname_id = int(info.geoname_id.values[0])
            iso_code = str(info.country_iso_code.values[0])
            geoip_name = str(info.geoip_name.values[0])
            un_name = str(info.un_name.values[0])
            country_name = str(info.country_name.values[0])

            entry = ISOCodeData.objects.get_or_create(geoname_id = geoname_id,
                                                    iso_code = iso_code,
                                                    geoip_name = geoip_name,
                                                    un_name = un_name,
                                                    country_name = country_name,)[0]
            entry.save()
            print('{} inserted into the models.ISOCodeData database'.format(item))
        print('Script executed succesfully!')
    except:
        print('Something went wrong! The script was not executed')
    finally:
        print('End of execution of the dbISOCodeData.py script')


if __name__ == '__main__':
    main()
