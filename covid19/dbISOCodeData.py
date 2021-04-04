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
            df_iso = pd.read_csv(os.path.join(config_filepath,file_name),header=0).dropna()
        else:
    	    raise FileNotFoundError('No configuration file {} found.'.format(file_name))

        db_del(ISOCodeData,confirm_before=False)
        print('Inserting all entries into models.ISOCodeData')

        list_of_iso_codes = df_iso['country_iso_code'].values
        print(list_of_iso_codes)

        for item in list_of_iso_codes:
            info = df_iso.loc[df_iso['country_iso_code']==item]
            print(info)

            # iso_code = info['country_iso_code'][0],
            entry = ISOCodeData.objects.get_or_create(geoname_id = info['geoname_id'][0],
                                                    iso_code = info['country_iso_code'][0],
                                                    geoip_name = info['geoip_name'][0],
                                                    un_name = info['un_name'][0],
                                                    country_name = info['country_name'][0])[0]
            entry.save()
        print('Script executed succesfully!')
    except:
        print('Something went wrong! The script was not executed')
    finally:
        print('End of execution of the dbISOCodeData.py script')


if __name__ == '__main__':
    main()
