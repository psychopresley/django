# To execute this file in the python shell just run the following
# command line: exec(open('populate_CountryInfo.py').read())

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE','covid19.settings')
django.setup()

from pandas import read_csv
from report.models import Country, CountryInfo

def main():
    def db_del(database,confirm_before=True):
        # This function delete all entries in "database" model

        flag = True

        if confirm_before:
            confirm_delete = input('This will erase all entries in models.CountryInfo. Press "n" if you wish to skip delete or any other key to continue: ')

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
        #  - aux2: Set 0, for reload database from 'countries_table.csv' file or 1 for update existing entries;
        #  - aux3: Set 1, for confirmation need in case aux1 is set to 0;

        config_filepath = r"C:\Users\user\Documents\GitHub\django\covid19\static\report\config"

        if 'config.csv' in os.listdir(config_filepath):
            print('Reading table from csv file')
            config = read_csv(os.path.join(config_filepath,'config.csv'),index_col='var').fillna('-')
        else:
    	    raise FileNotFoundError('No configuration file "config.csv" found.')

        task = config.loc['countryinfo_file'].aux1
        update = config.loc['countryinfo_file'].aux2
        confirm_value=config.loc['countryinfo_file'].aux3

        if not task:
            db_del(CountryInfo,confirm_before=confirm_value)

        else:
            country_table_file = os.path.join(config.loc['countryinfo_file'].file_path,
                                              config.loc['countryinfo_file'].file_name)

            countries_table = read_csv(country_table_file)
            countries_list = countries_table['Country'].unique()

            if update:
                print('updating all entries in models.CountryInfo')

                for item in countries_list:
                    info = countries_table.loc[countries_table['Country']==item]
                    country = CountryInfo.objects.get(country__name=item)

                    country.latitude = float(info.Latitude.values[0])
                    country.longitude = float(info.Longitude.values[0])
                    country.region = region=info.Region.values[0]
                    country.internet_code = info.internet_code.values[0]
                    country.map_image = info.map_image.values[0]

                    country.save()
                    print('{} updated in models.CountryInfo'.format(item))
            else:
                db_del(CountryInfo,confirm_before=confirm_value)

                print('Inserting all countries in the list to models.CountryInfo')

                for item in countries_list:
                    country = Country.objects.filter(name=item)
                    if country.exists():
                        info = countries_table.loc[countries_table['Country']==item]

                        entry = CountryInfo.objects.get_or_create(country=country[0],
                                                                  latitude=float(info.Latitude.values[0]),
                                                                  longitude=float(info.Longitude.values[0]),
                                                                  region=info.Region.values[0],
                                                                  internet_code=info.internet_code.values[0],
                                                                  map_image=info.map_image.values[0])[0]
                        entry.save()

                        print(item + ' inserted into models.CountryInfo')

        print('Script executed succesfully!')
    except:
        print('Something went wrong! The script was not executed')
    finally:
        print('End of execution of the populate_CountryInfo.py script')


if __name__ == '__main__':
    main()
