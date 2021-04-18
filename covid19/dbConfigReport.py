import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE','covid19.settings')
django.setup()

from pandas import read_csv
from time import time
from report.functions import *
from report.models import ConfigReport

def main():
    try:
        if dbconfig.task == 0:
            db_del(dbconfig.__name__,confirm_before=dbconfig.confirm_delete)
        else:
            countries_table = read_csv(dbconfig.aux_file_one,index_col='Country')

            print("Reading data file")
            df = read_json(dbconfig.base_file)

            print("Generating status report table")
            if dbconfig.task == 1:
                print('updating all entries in models.StatusReport')

                for item in countries_list:
                    info = status_report.loc[status_report['Country/Region']==item]
                    previous_info = previous_report.loc[previous_report['Country/Region']==item]
                    country = StatusReport.objects.get(country__name=item)

                    if previous_info.Confirmed_new_cases.values[0] == 0:
                        confirmed_new_pct_change = 0
                    else:
                        confirmed_new_pct_change = (info.Confirmed_new_cases.values[0] - previous_info.Confirmed_new_cases.values[0])*100/previous_info.Confirmed_new_cases.values[0]

                    if previous_info.Deaths_new_cases.values[0] == 0:
                        deaths_new_pct_change = 0
                    else:
                        deaths_new_pct_change = (info.Deaths_new_cases.values[0] - previous_info.Deaths_new_cases.values[0])*100/previous_info.Deaths_new_cases.values[0]

                    country.date=info.Date.values[0]
                    country.db_update=date.today()
                    country.confirmed=int(info.Confirmed.values[0])
                    country.confirmed_new=int(info.Confirmed_new_cases.values[0])
                    country.confirmed_new_short_avg=float(info.Confirmed_new_cases_short_avg.values[0])
                    country.confirmed_new_medium_avg=float(info.Confirmed_new_cases_medium_avg.values[0])
                    country.confirmed_new_long_avg=float(info.Confirmed_new_cases_long_avg.values[0])
                    country.confirmed_new_pct_change=float(confirmed_new_pct_change)
                    country.confirmed_pct_change=float(info['Confirmed_daily_%inc_by_country'].values[0])
                    country.confirmed_rank_region=int(info.Confirmed_rank_in_region.values[0])

                    country.save()
                    print('{} updated in models.{}'.format(item,dbconfig.__name__))
            else:
                db_del(dbconfig.__name__,confirm_before=dbconfig.confirm_delete)

                print('Inserting all entries in the list to models.{}'.format(dbconfig.__name__))
                for item in countries_list:
                    country = Country.objects.filter(name=item)

                    entry = StatusReport.objects.get_or_create(country=country[0],
                                                               date=info.Date.values[0],
                                                               db_update=date.today(),
                                                               confirmed=int(info.Confirmed.values[0]),
                                                               confirmed_new=int(info.Confirmed_new_cases.values[0]),
                                                               confirmed_new_short_avg=float(info.Confirmed_new_cases_short_avg.values[0]),
                                                               confirmed_new_medium_avg=float(info.Confirmed_new_cases_medium_avg.values[0]),
                                                               confirmed_new_long_avg=float(info.Confirmed_new_cases_long_avg.values[0]),
                                                               confirmed_new_pct_change=float(confirmed_new_pct_change),
                                                               confirmed_pct_change=float(info['Confirmed_daily_%inc_by_country'].values[0]),
                                                               confirmed_rank_region=int(info.Confirmed_rank_in_region.values[0]),
                                                               confirmed_rank_world=int(info.Confirmed_rank_in_world.values[0]),
                                                               confirmed_new_rank_region=int(info.Confirmed_new_cases_rank_in_region.values[0]),
                                                               confirmed_new_rank_world=int(info.Confirmed_new_cases_rank_in_world.values[0]),
                                                               confirmed_by_hundreds=float(info['Confirmed_by_100k'].values[0]),
                                                               confirmed_by_hundreds_rank_region=int(info['Confirmed_by_100k_rank_region'].values[0]),
                                                               confirmed_by_hundreds_rank_world=int(info['Confirmed_by_100k_rank_world'].values[0]),
                                                               deaths=int(info.Deaths.values[0]),
                                                               deaths_new=int(info.Deaths_new_cases.values[0]),
                                                               deaths_new_short_avg=float(info.Deaths_new_cases_short_avg.values[0]),
                                                               deaths_new_medium_avg=float(info.Deaths_new_cases_medium_avg.values[0]),
                                                               deaths_new_long_avg=float(info.Deaths_new_cases_long_avg.values[0]),
                                                               deaths_new_pct_change=float(deaths_new_pct_change),
                                                               deaths_pct_change=float(info['Deaths_daily_%inc_by_country'].values[0]),
                                                               deaths_rank_region=int(info.Deaths_rank_in_region.values[0]),
                                                               deaths_rank_world=int(info.Deaths_rank_in_world.values[0]),
                                                               deaths_new_rank_region=int(info.Deaths_new_cases_rank_in_region.values[0]),
                                                               deaths_new_rank_world=int(info.Deaths_new_cases_rank_in_world.values[0]),
                                                               deaths_by_hundreds=float(info['Deaths_by_100k'].values[0]),
                                                               deaths_by_hundreds_rank_region=int(info['Deaths_by_100k_rank_region'].values[0]),
                                                               deaths_by_hundreds_rank_world=int(info['Deaths_by_100k_rank_world'].values[0]),
                                                               recovered=int(info.Recovered.values[0]),
                                                               recovered_new=int(info.Recovered_new_cases.values[0]),
                                                               recovered_new_short_avg=float(info.Recovered_new_cases_short_avg.values[0]),
                                                               recovered_new_medium_avg=float(info.Recovered_new_cases_medium_avg.values[0]),
                                                               recovered_new_long_avg=float(info.Recovered_new_cases_long_avg.values[0]),
                                                               recovered_pct_change=float(info['Recovered_daily_%inc_by_country'].values[0]),
                                                               recovered_rank_region=int(info.Recovered_rank_in_region.values[0]),
                                                               recovered_rank_world=int(info.Recovered_rank_in_world.values[0]),
                                                               recovered_new_rank_region=int(info.Recovered_new_cases_rank_in_region.values[0]),
                                                               recovered_new_rank_world=int(info.Recovered_new_cases_rank_in_world.values[0]),
                                                               recovered_by_hundreds=float(info['Recovered_by_100k'].values[0]),
                                                               recovered_by_hundreds_rank_region=int(info['Recovered_by_100k_rank_region'].values[0]),
                                                               recovered_by_hundreds_rank_world=int(info['Recovered_by_100k_rank_world'].values[0]),
                                                               active=int(info.Active.values[0]),
                                                               active_new=int(info.Active_new_cases.values[0]),
                                                               active_new_short_avg=float(info.Active_new_cases_short_avg.values[0]),
                                                               active_new_medium_avg=float(info.Active_new_cases_medium_avg.values[0]),
                                                               active_new_long_avg=float(info.Active_new_cases_long_avg.values[0]),
                                                               active_pct=float(info.active_pct.values[0]),
                                                               active_pct_change=float(info['Active_daily_%inc_by_country'].values[0]),
                                                               active_rank_region=int(info.Active_rank_in_region.values[0]),
                                                               active_rank_world=int(info.Active_rank_in_world.values[0]),
                                                               active_new_rank_region=int(info.Active_new_cases_rank_in_region.values[0]),
                                                               active_new_rank_world=int(info.Active_new_cases_rank_in_world.values[0]),
                                                               active_by_hundreds=float(info['Active_by_100k'].values[0]),
                                                               active_by_hundreds_rank_region=int(info['Active_by_100k_rank_region'].values[0]),
                                                               active_by_hundreds_rank_world=int(info['Active_by_100k_rank_world'].values[0]),
                                                               mortality_rank_region=int(info.mortality_rank_region.values[0]),
                                                               mortality_rank_world=int(info.mortality_rank_world.values[0]),
                                                               mortality=float(info.mortality.values[0]),
                                                               mortality_quartile=info.mortality_quartile.values[0],
                                                               mortality_quartile_position=info.mortality_quartile_position.values[0],)[0]

                        entry.save()
                        print('{} inserted into models.StatusReport'.format(item))
                    else:
                        print(item + ' is not on StatusReport.models')

        dbconfig.log_status=1
    except:
        dbconfig.log_status=2
    finally:
        print('End of {} script'.format(os.path.basename(__file__)))


if __name__ == '__main__':

    script_start_time = time()
    main()

    dbconfig.time_exec=round(time()-script_start_time,2)
    dbconfig.save()
