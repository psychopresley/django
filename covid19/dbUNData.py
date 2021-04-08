import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE','covid19.settings')
django.setup()

import pandas as pd
from report.models import UNData

def undata(df_un,drop_columns=None,Year='latest'):

    if Year=='latest':
        df=df_un[df_un.Year==max(df_un.Year)].copy()
    else:
        df=df_un[df_un.Year==Year].copy

    if drop_columns != None:
        df.drop(drop_columns,axis='columns',inplace=True)

    return df

def clean_undata(df_un):

    df=pd.DataFrame([])
    for country in df_un['Country/Region'].unique():
        df_country = df_un[df_un['Country/Region']==country]
        df=pd.concat([df,df_country.pivot(index='Country/Region', columns='Series', values='Value').reset_index()])
        df=df.fillna(value=0)

    return df

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
        file_name = 'UNData.csv'

        if file_name in os.listdir(config_filepath):
            print('Reading configuration file')
            config = pd.read_csv(os.path.join(config_filepath,file_name)).fillna('-')
        else:
    	    raise FileNotFoundError('No configuration file {} found.'.format(file_name))

        df=pd.read_csv(file_name)
        drop_columns = ['Year','Footnotes','Source']

        df_un=undata(df,drop_columns)
        df_cleaned = clean_undata(df_un)

        db_del(UNData,confirm_before=False)

        print('Inserting all entries in the UN dataframe into models.UNData')

        for item in df_cleaned['Country/Region'].values:
            info = df_cleaned.loc[df_cleaned['Country/Region']==item]

            entry = UNData.objects.get_or_create(country = info['Country/Region'][0],
                                                 population = info['Population mid-year estimates (millions)'][0],
                                                 density = info['Population density'][0],
                                                 population_male = info['Population mid-year estimates for males (millions)'][0],
                                                 population_female = info['Population mid-year estimates for females (millions)'][0],
                                                 sex_ratio = info['Sex ratio (males per 100 females)'][0],
                                                 pct_minus_fourteen = info['Population aged 0 to 14 years old (percentage)'][0],
                                                 pct_plus_sixty = info['Population aged 60+ years old (percentage)'][0])[0]
            entry.save()

            print(item + ' inserted into models.UNData')

        print('Script executed succesfully!')
    except:
        print('Something went wrong! The script was not executed')
    finally:
        print('End of execution of the dbUNData.py script')


if __name__ == '__main__':
    main()
