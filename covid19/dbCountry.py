import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE','covid19.settings')
django.setup()

from pandas import read_json, read_csv
from time import ctime
from report.models import Country

def main():
    def db_del(database,confirm_before=True):
        # This function delete all entries in "database" model

        flag = True

        if confirm_before:
            confirm_delete = input('This will erase all entries in models.Country. Press "n" if you wish to skip delete or any other key to continue: ')

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

        log_dbCountry=[]
        log_dbCountry.append('\n----------dbCountry.py SCRIPT EXECUTION REPORT-----------\n')
        log_dbCountry.append('\n'+ '--> Local time: ' + ctime() + '\n\n')

        config_filepath = r"C:\Users\user\Documents\GitHub\django\covid19\static\report\config"

        if 'config.csv' in os.listdir(config_filepath):
            print('Reading configuration file')
            config = read_csv(os.path.join(config_filepath,'config.csv'),index_col='var').fillna('-')
        else:
    	    raise FileNotFoundError('No configuration file "config.csv" found.')

        task = config.loc['status_report'].aux1
        confirm_value=config.loc['status_report'].aux3

        if not task:
            db_del(Country,confirm_before=confirm_value)
        else:
            print("Reading 'country_report.json' file")

            country_report = os.path.join(config.loc['status_report'].file_path,
                                          config.loc['status_report'].file_name)

            df = read_json(country_report)
            countries_list = df['Country/Region'].unique()

            label_map_file = os.path.join(config.loc['labelmap_file'].file_path,
                                          config.loc['labelmap_file'].file_name)

            label_map = read_csv(label_map_file,header=None,index_col=0)

            # reading label map dictionary:
            label_dict = label_map.to_dict()[1]
            df['Country/Region'] = df['Country/Region'].transform(lambda x: label_dict[x] if x in label_dict.keys() else x)

            log_dbCountry.append('\n - Most recent date on report: {}'.format(max(df.Date)))

            db_del(Country,confirm_before=confirm_value)
            print('Inserting all countries in the list to models.Country')

            for country in countries_list:
                entry = Country.objects.get_or_create(name=country)[0]
                entry.save()

                print('{} inserted into models.Country'.format(country))

        message = 'Script executed succesfully!'
        print(message)
        log_dbCountry.append('\n - {}'.format(message))
    except:
        message = 'Something went wrong! The script was not executed'
        print(message)
        log_dbCountry.append('\n {}'.format(message))
    finally:
        message = 'End of execution of the populate_Country.py script'
        print(message)
        log_dbCountry.append('\n {}'.format(message))

        log_dir = r'C:\Users\user\Documents\GitHub\django\covid19\static\report\log'
        os.chdir(log_dir)

        log = open('log_dbCountry.txt','w')
        log.writelines(log_dbCountry)
        log.close()


if __name__ == '__main__':
    main()
