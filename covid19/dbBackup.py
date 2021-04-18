import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE','covid19.settings')
django.setup()

import pandas as pd
from report.models import *

def db_backup(database):
    dbconfig = database.objects.all()
    df=pd.DataFrame()

    for obj in dbconfig:
        df_aux=pd.DataFrame()
        for k,v in obj.__dict__.items():
            df_aux[k]=[v]
        df=pd.concat([df,df_aux.drop(['_state'],axis=1)])

    df.to_csv('{}_{}.csv'.format('backup',database.__name__),index=False)

if __name__ == '__main__':

    # Retieving database info:
    x=input('''
Enter the number corresponding to the database for backup file or press any
other key to exit script:
0 - All
1 - Country;
2 - ConfigReport;
3 - UNData
4 - ISOCodeData

Enter number:
''')

    try:
        models = [Country, ConfigReport, UNData, ISOCodeData]
        if x == '0':
            for model in models:
                db_backup(model)
        elif x in [str(i) for i in list(range(1,5))]:
            database = models[int(x)-1]
            db_backup(database)
        else:
            pass

        print('Script executed successfully!')
    except:
        print('Something wrong in the script. No actions taken.')
    finally:
        print('End of {} execution'.format(os.path.basename(__file__)))
