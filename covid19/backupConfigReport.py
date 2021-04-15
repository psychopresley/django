import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE','covid19.settings')
django.setup()

import pandas as pd
from report.models import ConfigReport


if __name__ == '__main__':

    # Retieving configuration info:
    dbconfig = ConfigReport.objects.all()
    df=pd.DataFrame()

    for obj in dbconfig:
        df_aux=pd.DataFrame()
        for k,v in obj.__dict__.items():
            df_aux[k]=[v]
        df=pd.concat([df,df_aux.drop(['_state'],axis=1)])

    df.to_csv('config.csv',index=False)
