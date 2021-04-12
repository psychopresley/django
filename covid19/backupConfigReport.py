import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE','covid19.settings')
django.setup()

import pandas as pd
from report.models import ConfigReport


if __name__ == '__main__':

    # Retieving configuration info:
    dbconfig = ConfigReport.objects.all()

    for obj in dbconfig:
        df=pd.DataFrame()
        columns = []
        values = []

        for k,v in obj.__dict__.items():
            columns.append(k)
            values.append(v)

        df=pd.DataFrame(data=values,columns = columns)
        # series = pd.Series(obj.__dict__)
        # df = pd.concat([df,pd.DataFrame(series,columns=[series.var_name]).drop(['_state','var_name'])],axis=1)

    print(df)
    # print(values)
