import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE','covid19.settings')
django.setup()

import pandas as pd
from pathlib import Path
from report.models import StatusReport, ISOCodeData, UNData

if __name__ == '__main__':
    try:
        exception_list = ['Cruise Ship','Taiwan'] # Countries that are not on UN database

        # Initializing the array for statistics variables:
        countries = StatusReport.objects.all()
        pct_plus_sixty = []
        density=[]
        confirmed_by_hundreds = []
        deaths_by_hundreds = []
        mortality = []
        labels = []

        # CREATING ARRAYS FOR THE DEFINED VARIABLES:
        for obj in countries:
            if obj.country.name in exception_list:
                pass
            else:
                #RETRIEVING THE COUNTRY'S COVID-19 STATISTICS FROM THE STATUS REPORT
                labels.append(obj.country.name)
                mortality.append(obj.mortality*100)
                deaths_by_hundreds.append(obj.deaths_by_hundreds)
                confirmed_by_hundreds.append(obj.confirmed_by_hundreds)

                # RETRIEVING THE COUNTRY'S UN DATA:
                x = ISOCodeData.objects.get(country_name=obj.country.name)
                x = UNData.objects.get(country=x.un_name)
                pct_plus_sixty.append(x.pct_plus_sixty)
                density.append(x.density)

        # CREATING THE DATAFRAME:
        df = pd.DataFrame(data={
        'country':labels,
        'density':density,
        'population +60':pct_plus_sixty,
        'mortality':mortality,
        'confirmed/100k':confirmed_by_hundreds,
        'deaths/100k':deaths_by_hundreds,
        })

        for column in ['density','mortality','confirmed/100k','deaths/100k']:
            quantiles = df[column].quantile([0.25,0.75])
            IQR = quantiles[0.75] - quantiles[0.25]

            outliers = [quantiles[0.25]-1.5*IQR,quantiles[0.75]+1.5*IQR]
            df[column+'_outlier'] = df[column].apply(lambda x:1 if (x < outliers[0] or x > outliers[1]) else 0)

        print('Script executed correctly!')
    except:
        print('Something wrong in the script. No actions taken.')
    finally:
        curr_dir = os.getcwd()
        sub_dir = '/report/statistics'

        save_dir = curr_dir + sub_dir

        os.chdir(save_dir)
        df.to_json('statistics.json')

        print('End of {} execution'.format(os.path.basename(__file__)))
