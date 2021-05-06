# Importing django modules, forms and models:
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View,TemplateView
from pathlib import Path
from . import forms
from .functions import *
from report.models import StatusReport, MonthReport, WeekReport, ISOCodeData, UNData, ConfigReport

# Importing plotly modules:
import plotly.graph_objs as go
import plotly.express as px
from plotly.offline import plot
from plotly.subplots import make_subplots

# Importing geoip2 and correlated modules:
from geoip2.database import Reader
from socket import gethostbyname, getfqdn
import requests

# Include the `fusioncharts.py` file that contains functions to embed the charts.
# Fusion charts tutorial: https://www.fusioncharts.com/django-charts?framework=django
from . import fusioncharts as fsn

# Importing python native modules:
import os
import numpy as np
import pandas as pd
from calendar import week
from datetime import datetime, timedelta
from collections import OrderedDict
from sklearn.linear_model import LinearRegression, TheilSenRegressor, RANSACRegressor, HuberRegressor
from sklearn.metrics import mean_squared_error, r2_score


# creating the reader to use in getIP(reader) function:
curr_dir = os.path.dirname(__file__)
geoip_dir = 'geoip_db'
geoip_file = 'GeoLite2-Country.mmdb'

if geoip_dir in os.listdir(curr_dir):
    lookup_dir = os.path.join(curr_dir,geoip_dir)
    if geoip_file in os.listdir(lookup_dir):
        geoip_db = os.path.join(lookup_dir,geoip_file)
    else:
        raise FileNotFoundError('Not found GeoLite2-Country.mmdb file in geoip_db directory.')
else:
    raise FileNotFoundError('No directory "geoip_db" found.')

reader = Reader(geoip_db)
countries_in_db = [y.country.name for y in StatusReport.objects.all()]
statistics_file = curr_dir + '/statistics/statistics.json'


# Create your views here.

# THIS IS THE HOME (INDEX) PAGE:

class IndexView(TemplateView):
    template_name = 'report/index.html'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)

        form = forms.SelectCountry()
        selected_country = form['country'].initial

        context['nav_index'] = 'navbar-item-active'
        context['db_update'] = StatusReport.objects.order_by('-db_update')[0].db_update
        context['form'] = form

        for item in ['confirmed','deaths','recovered','active']:
            total=0
            total_new=0
            for obj in StatusReport.objects.all():
                total += obj.__dict__[item]
                total_new += obj.__dict__[item+'_new']

            context[item] = total
            context[item+'_new'] = total_new

            top_ten_new_confirmed = StatusReport.objects.all().order_by('confirmed_new_rank_world')[:10]
            top_ten_new_deaths = StatusReport.objects.all().order_by('deaths_new_rank_world')[:10]
            top_ten_confirmed_by_hundreds = StatusReport.objects.all().order_by('-confirmed_by_hundreds')[:10]
            top_ten_deaths_by_hundreds = StatusReport.objects.all().order_by('-deaths_by_hundreds')[:10]

            dict_confirmed={}
            for obj in top_ten_new_confirmed:
                dict_confirmed={**dict_confirmed,**{obj.__str__():obj.__dict__['confirmed_new']}}

            dict_deaths={}
            for obj in top_ten_new_deaths:
                dict_deaths={**dict_deaths,**{obj.__str__():obj.__dict__['deaths_new']}}

            dict_confirmed_by_hundreds={}
            for obj in top_ten_confirmed_by_hundreds:
                dict_confirmed_by_hundreds={**dict_confirmed_by_hundreds,**{obj.__str__():obj.__dict__['confirmed_by_hundreds']}}

            dict_deaths_by_hundreds={}
            for obj in top_ten_deaths_by_hundreds:
                dict_deaths_by_hundreds={**dict_deaths_by_hundreds,**{obj.__str__():obj.__dict__['deaths_by_hundreds']}}

            context['top_ten_new_confirmed'] = dict_confirmed
            context['top_ten_new_deaths'] = dict_deaths
            context['top_ten_confirmed_by_hundreds'] = dict_confirmed_by_hundreds
            context['top_ten_deaths_by_hundreds'] = dict_deaths_by_hundreds

        return context


class StatisticsView(TemplateView):
    template_name = 'report/statistics.html'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)

        context['nav_statistics'] = 'navbar-item-active'
        context['db_update'] = StatusReport.objects.order_by('-db_update')[0].db_update

        for item in ['confirmed','deaths']:
            total=0
            total_new=0
            for obj in StatusReport.objects.all():
                total += obj.__dict__[item]
                total_new += obj.__dict__[item+'_new']

            context[item] = total
            context[item+'_new'] = total_new


        # Creating the Top10 data:

        top_ten_confirmed = StatusReport.objects.all().order_by('-confirmed')[:10]
        plot_confirmedbar = top_ten_bar(top_ten_confirmed,
                                        'confirmed',
                                        title='Total confirmed cases')

        top_ten_new_confirmed = StatusReport.objects.all().order_by('confirmed_new_rank_world')[:10]
        plot_newconfirmedbar = top_ten_bar(top_ten_new_confirmed,
                                           'confirmed_new',
                                           title='Confirmed cases (Last 24h)')

        top_ten_confirmed_by_hundreds = StatusReport.objects.all().order_by('-confirmed_by_hundreds')[:10]
        plot_confirmedbyhundredsbar = top_ten_bar(top_ten_confirmed_by_hundreds,
                                                  'confirmed_by_hundreds',
                                                  title='Confirmed cases / 100k habitants')

        top_ten_confirmed_new_by_hundreds = StatusReport.objects.all().order_by('-confirmed_new_by_hundreds')[:10]
        plot_confirmednewbyhundredsbar = top_ten_bar(top_ten_confirmed_new_by_hundreds,
                                                     'confirmed_new_by_hundreds',
                                                     title='Confirmed cases (Last 24h) / 100k habitants')

        top_ten_deaths = StatusReport.objects.all().order_by('-deaths')[:10]
        top_ten_new_deaths = StatusReport.objects.all().order_by('deaths_new_rank_world')[:10]
        top_ten_deaths_by_hundreds = StatusReport.objects.all().order_by('-deaths_by_hundreds')[:10]
        top_ten_deaths_new_by_hundreds = StatusReport.objects.all().order_by('-deaths_new_by_hundreds')[:10]


        dict_confirmed={}
        total_confirmed_top_ten = 0
        for obj in top_ten_confirmed:
            dict_confirmed={**dict_confirmed,**{obj.__str__():obj.__dict__['confirmed']}}
            total_confirmed_top_ten += obj.__dict__['confirmed']

        dict_deaths={}
        total_deaths_top_ten = 0
        for obj in top_ten_deaths:
            dict_deaths={**dict_deaths,**{obj.__str__():obj.__dict__['deaths']}}
            total_deaths_top_ten += obj.__dict__['deaths']

        dict_confirmed_new={}
        total_new_confirmed_top_ten = 0
        for obj in top_ten_new_confirmed:
            dict_confirmed_new={**dict_confirmed_new,**{obj.__str__():obj.__dict__['confirmed_new']}}
            total_new_confirmed_top_ten += obj.__dict__['confirmed_new']

        dict_deaths_new={}
        total_new_deaths_top_ten = 0
        for obj in top_ten_new_deaths:
            dict_deaths_new={**dict_deaths_new,**{obj.__str__():obj.__dict__['deaths_new']}}
            total_new_deaths_top_ten += obj.__dict__['deaths_new']

        dict_confirmed_by_hundreds={}
        for obj in top_ten_confirmed_by_hundreds:
            dict_confirmed_by_hundreds={**dict_confirmed_by_hundreds,**{obj.__str__():obj.__dict__['confirmed_by_hundreds']}}

        dict_deaths_by_hundreds={}
        for obj in top_ten_deaths_by_hundreds:
            dict_deaths_by_hundreds={**dict_deaths_by_hundreds,**{obj.__str__():obj.__dict__['deaths_by_hundreds']}}

        dict_confirmed_new_by_hundreds={}
        for obj in top_ten_confirmed_new_by_hundreds:
            dict_confirmed_new_by_hundreds={**dict_confirmed_new_by_hundreds,**{obj.__str__():obj.__dict__['confirmed_new_by_hundreds']}}

        dict_deaths_new_by_hundreds={}
        for obj in top_ten_deaths_new_by_hundreds:
            dict_deaths_new_by_hundreds={**dict_deaths_new_by_hundreds,**{obj.__str__():obj.__dict__['deaths_new_by_hundreds']}}

        # CREATING THE UN DATA VARIABLES FOR PLOT:

        # 1 - Reading statistics table:
        df = pd.read_json(statistics_file)

        # 2 - Retrieving plot variables:

        # 2.1 - populational density as independent variable:

        # removing outliers for the populational density:
        df_density = df[df['density_outlier']==0]

        # 2.1.1 - confirmed/100k plot:
        df_aux = df_density[df_density['confirmed/100k_outlier']==0]

        labels = df_aux['country']
        xdata=df_aux['density'].values
        ydata=df_aux['confirmed/100k'].values

        sct_1 = scatter_undata(xdata,ydata,labels,
                               xtext='Population density (hab/km²)',
                               ytext='Confirmed cases/100k habitants',
                               with_fit=True,
                               fit_intercept=False)

        # 2.1.2 - deaths/100k plot:
        df_aux = df_density[df_density['deaths/100k_outlier']==0]

        labels = df_aux['country']
        xdata=df_aux['density'].values
        ydata=df_aux['deaths/100k'].values

        scatter_deaths_density = scatter_undata(xdata,ydata,labels,
                                                xtext='Population density (hab/km²)',
                                                ytext='Deaths/100k habitants',
                                                with_fit=True,
                                                fit_intercept=False)

        # 2.1.3 - Mortality plot:
        df_aux = df_density[df_density['mortality_outlier']==0]

        labels = df_aux['country']
        xdata=df_aux['density'].values
        ydata=df_aux['mortality'].values

        scatter_mortality_density = scatter_undata(xdata,ydata,labels,
                                                   xtext='Population density (hab/km²)',
                                                   ytext='Mortality',
                                                   with_fit=True,
                                                   fit_intercept=False)

        # 2.2 - population over 60yrs as independent variable:

        # 2.2.1 - confirmed/100k plot:
        df_aux = df[df['confirmed/100k_outlier']==0]

        labels = df_aux['country']
        xdata=df_aux['population +60'].values
        ydata=df_aux['confirmed/100k'].values


        # Scatter plot with linear regression model:
        scatter_confirmed_over_sixty = scatter_undata(xdata,ydata,labels,
                                                   xtext='% of population over 60 years',
                                                   ytext='Confirmed cases/100k habitants',
                                                   with_fit=True)


        # 2.2.2 - deaths/100k plot:
        df_aux = df[df['deaths/100k_outlier']==0]

        labels = df_aux['country']
        xdata=df_aux['population +60'].values
        ydata=df_aux['deaths/100k'].values
        y2data=df_aux['mortality'].values

        scatter_deaths_over_sixty = scatter_undata(xdata,ydata,labels,
                                                   xtext='% of population over 60 years',
                                                   ytext='Deaths/100k habitants',
                                                   with_fit=True)

        # 2.2.3 - Mortality plot:
        df_aux = df[df['mortality_outlier']==0]

        labels = df_aux['country']
        xdata=df_aux['population +60'].values
        ydata=df_aux['mortality'].values

        scatter_mortality_over_sixty = scatter_undata(xdata,ydata,labels,
                                                   xtext='% of population over 60 years',
                                                   ytext='Mortality',
                                                   with_fit=True)

        # 2.3 - Perfet correlation example: Confirmed/100k vs Deaths/100k:

        df_aux = df[df['confirmed/100k_outlier']==0]

        labels = df_aux['country']
        xdata=df_aux['confirmed/100k'].values
        ydata=df_aux['deaths/100k'].values

        scatter_deaths_vs_confirmed = scatter_undata(xdata,ydata,labels,
                                                     xtext='Confirmed cases / 100k habitants',
                                                     ytext='Deaths / 100k habitants',
                                                     with_fit=True)


        # PASSING ALL DATA TO CONTEXT:

        context['world_population'] = UNData.objects.get(country__startswith='Total').population
        context['total_confirmed_top_ten'] = total_confirmed_top_ten
        context['total_new_confirmed_top_ten'] = total_new_confirmed_top_ten
        context['total_deaths_top_ten'] = total_deaths_top_ten
        context['total_new_deaths_top_ten'] = total_new_deaths_top_ten
        context['top_ten_confirmed'] = dict_confirmed
        context['top_ten_deaths'] = dict_deaths
        context['top_ten_new_confirmed'] = dict_confirmed_new
        context['top_ten_new_deaths'] = dict_deaths_new
        context['top_ten_confirmed_by_hundreds'] = dict_confirmed_by_hundreds
        context['top_ten_deaths_by_hundreds'] = dict_deaths_by_hundreds
        context['top_ten_confirmed_new_by_hundreds'] = dict_confirmed_new_by_hundreds
        context['top_ten_deaths_new_by_hundreds'] = dict_deaths_new_by_hundreds
        context['top_ten_deaths_new_by_hundreds'] = dict_deaths_new_by_hundreds
        context['scatter_confirmed_over_sixty'] = scatter_confirmed_over_sixty
        context['scatter_confirmed_density'] = sct_1
        context['scatter_deaths_over_sixty'] = scatter_deaths_over_sixty
        context['scatter_deaths_density'] = scatter_deaths_density
        context['scatter_mortality_over_sixty'] = scatter_mortality_over_sixty
        context['scatter_mortality_density'] = scatter_mortality_density
        context['scatter_deaths_vs_confirmed'] = scatter_deaths_vs_confirmed
        context['plot_confirmedbyhundredsbar'] = plot_confirmedbyhundredsbar
        context['plot_confirmednewbyhundredsbar'] = plot_confirmednewbyhundredsbar
        context['plot_newconfirmedbar'] = plot_newconfirmedbar
        context['plot_confirmedbar'] = plot_confirmedbar

        return context


class ReadMeView(TemplateView):
    template_name = 'report/read_me.html'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['nav_readme'] = 'navbar-item-active'

        form = forms.SelectCountry()
        selected_country = form['country'].initial
        context['form'] = form

        return context


def countriespage(request):
    form = forms.SelectCountry()

    # Checking the request IP and redirect to display the country to which
    # it belongs:
    x = ISOCodeData.objects.get(iso_code=getIP(reader).iso_code)
    if x.country_name in countries_in_db:
        selected_country = x.country_name
        form['country'].initial = selected_country
    else:
        selected_country = form['country'].initial


    # Checking if this is a user select request
    if request.method == 'POST':
        form = forms.SelectCountry(request.POST);

        if form.is_valid():
            selected_country = form.cleaned_data['country'];

    for item in ['confirmed','deaths']:
        total=0
        world_dict={}
        for obj in StatusReport.objects.all():
            total += obj.__dict__[item]

        world_dict = {**world_dict,**{item+'_world':total}}

    status = StatusReport.objects.get(country=selected_country)
    month_report = MonthReport.objects.filter(country=selected_country).order_by('-month')
    week_report = WeekReport.objects.filter(country=selected_country).order_by('-week')

    # RETRIEVING THE COUNTRY'S UN DATA:
    x = ISOCodeData.objects.get(country_name=selected_country)
    country_info = UNData.objects.get(country=x.un_name).__dict__
    # country_info = UNData.objects.get(country=selected_country).__dict__

    # PASSING STATUSREPORT MODEL VARIABLES AS TEMPLATE TAGS
    mortality_quartile_list=[]
    confirmed_quartile_list=[]
    deaths_quartile_list=[]

    for quartile in ['1st','2nd','3rd','4th']:
        mortality_lower_bound = min(StatusReport.objects.filter(mortality_quartile__startswith=quartile).values_list('mortality'))[0]
        confirmed_lower_bound = min(StatusReport.objects.filter(confirmed_by_hundreds_quartile__startswith=quartile).values_list('confirmed_by_hundreds'))[0]
        deaths_lower_bound = min(StatusReport.objects.filter(deaths_by_hundreds_quartile__startswith=quartile).values_list('deaths_by_hundreds'))[0]

        mortality_quartile_list.append(mortality_lower_bound)
        confirmed_quartile_list.append(confirmed_lower_bound)
        deaths_quartile_list.append(deaths_lower_bound)


    status_dict = {'country_coord':status.country._coordinates_(),
                   'report_date':status.date,
                   'db_update':status.db_update,
                   'mortality_quartile_list':mortality_quartile_list,
                   'confirmed_quartile_list':confirmed_quartile_list,
                   'deaths_quartile_list':deaths_quartile_list,
                   **world_dict,
                   **country_info,
                   **status.country.__dict__,
                  }

    for k,v in status.__dict__.items():
        status_dict = {**status_dict,**{k:status.__dict__[k]}}


    # PASSING MONTHREPORT MODEL VARIABLES AS TEMPLATE TAGS
    month_report_dict = {
                         'month':[],'last_update':[],
                         'confirmed_month':[],'confirmed_pct_change_month':[],
                         'confirmed_rank_region_month':[],'confirmed_rank_world_month':[],
                         'deaths_month':[],'deaths_pct_change_month':[],
                         'deaths_rank_region_month':[],'deaths_rank_world_month':[],
                        }

    rows=[]
    x_month=[]
    y_confirmed=[]
    y_deaths=[]
    idx=0

    for obj in month_report:
        dict={}
        for key in month_report_dict.keys():
            dict[key]=obj.__dict__[key.replace('_month','')]
        dict = {**dict,**{'idx':idx,'days_in_month':obj.__dict__['days_in_month']}}

        x_month.append(obj.__dict__['month'])
        y_deaths.append(obj.__dict__['deaths'])
        y_confirmed.append(obj.__dict__['confirmed'])

        idx += 1
        rows.append(dict)

    deaths_prediction = int(month_report[0].deaths*(month_report[0].days_in_month)/month_report[0].last_update.day)
    confirmed_prediction = int(month_report[0].confirmed*(month_report[0].days_in_month)/month_report[0].last_update.day)

    if month_report[1].confirmed > 0:
        confirmed_prediction_pct = (confirmed_prediction - month_report[1].confirmed)/month_report[1].confirmed
    else:
        confirmed_prediction_pct = 0

    if month_report[1].deaths > 0:
        deaths_prediction_pct = (deaths_prediction - month_report[1].deaths)/month_report[1].deaths
    else:
        deaths_prediction_pct = 0

    month_dict = {'month_rows':rows,
                  'month_header':['','Confirmed','Rank (Region - World)','Deaths','Rank (Region - World)'],
                  'confirmed_prediction':confirmed_prediction,
                  'deaths_prediction':deaths_prediction,
                  'confirmed_prediction_pct':confirmed_prediction_pct,
                  'deaths_prediction_pct':deaths_prediction_pct,
                  }


# ==============================================================================
# ==============================================================================

    # ADDING SOME CHARTS:
    # Here's a nice page if you wish to know more about plotly + django:
    # https://www.codingwithricky.com/2019/08/28/easy-django-plotly/
    # colorscales code: https://plotly.com/python/builtin-colorscales/


    # # 1 - MONTH REPORT CHARTS:
    subplot1data = (x_month[::-1],y_confirmed[::-1])
    subplot2data = (x_month[::-1],y_deaths[::-1])

    plot_month = month_subplot(subplot1data,subplot2data,['Confirmed','Deaths'])

# ==============================================================================
# ==============================================================================

    # PASSING WEEKREPORT MODEL VARIABLES AS TEMPLATE TAGS
    week_report_dict = {
                         'week':[],'last_update':[],
                         'confirmed_week':[],'confirmed_pct_change_week':[],
                         'confirmed_rank_region_week':[],'confirmed_rank_world_week':[],
                         'deaths_week':[],'deaths_pct_change_week':[],
                         'deaths_rank_region_week':[],'deaths_rank_world_week':[],
                        }

    rows_week=[]
    x_week=[]
    y_confirmed_week=[]
    y_deaths_week=[]
    idx=0

    for obj in week_report:
        dict={}
        for key in week_report_dict.keys():
            dict[key]=obj.__dict__[key.replace('_week','')]
        week = obj.__dict__['week']
        dict = {**dict,**{'idx':idx,'week_range':start_end_week(week[:4], week[-2:])}}

        if week.endswith('00'):
            pass
        else:
            x_week.append(week)
            y_deaths_week.append(obj.__dict__['deaths'])
            y_confirmed_week.append(obj.__dict__['confirmed'])

        idx += 1
        rows_week.append(dict)

    week_dict = {'week_rows':rows_week,
                 'week_header':['','Week','Confirmed','Rank (Region - World)','Deaths','Rank (Region - World)'],
                 }

# ==============================================================================
# ==============================================================================

    # ADDING SOME CHARTS:
    # Here's a nice page if you wish to know more about plotly + django:
    # https://www.codingwithricky.com/2019/08/28/easy-django-plotly/
    # colorscales code: https://plotly.com/python/builtin-colorscales/

    # 2 - WEEK REPORT CHARTS:
    subplot1data = (x_week[::-1],y_confirmed_week[::-1])
    subplot2data = (x_week[::-1],y_deaths_week[::-1])

    plot_week = week_subplot(subplot1data,subplot2data,labels=['Confirmed','Deaths'])
    plot_heatmap_week = heatmap_subplot(subplot1data,subplot2data,labels=['Confirmed','Deaths'])
    plot_histogram = density_plot(y_deaths_week[::-1],y_confirmed_week[::-1])


    # 3 - FUSIONCHARTS ANGULAR GAUGE:
    # plot_mortality_gauge = fusion_gauge(status.mortality_quartile_position*100,'Mortality')
    plot_mortality_gauge = quartiles_gauge(status.mortality*100,
                                           status.mortality_quartile,
                                           status.mortality_quartile_position,
                                           text='Mortality',)

    plot_confirmedbyhundreds_gauge = quartiles_gauge(status.confirmed_by_hundreds,
                                                     status.confirmed_by_hundreds_quartile,
                                                     status.confirmed_by_hundreds_quartile_position,
                                                     text='Confirmed/100k',
                                                     suffix='',
                                                     precision=0)

    plot_deathsbyhundreds_gauge = quartiles_gauge(status.deaths_by_hundreds,
                                                  status.deaths_by_hundreds_quartile,
                                                  status.deaths_by_hundreds_quartile_position,
                                                  text='Deaths/100k',
                                                  suffix='',
                                                  precision=0)

    plot_deathsbyhundreds_rank = rank_bullets(status.deaths_by_hundreds_rank_world,
                                              range=[0,100],
                                              text='World')

    plot_dict = {
    'plot_month':plot_month,
    'plot_week':plot_week,
    'plot_heatmap_week':plot_heatmap_week,
    'plot_histogram':plot_histogram,
    'plot_mortality_gauge':plot_mortality_gauge,
    'plot_confirmedbyhundreds_gauge':plot_confirmedbyhundreds_gauge,
    'plot_deathsbyhundreds_gauge':plot_deathsbyhundreds_gauge,
    'plot_deathsbyhundreds_rank':plot_deathsbyhundreds_rank,
    }

    return render(request,'report/countries.html',
                  {'form':form,
                  'nav_countries':'navbar-item-active',
                  **plot_dict,
                  **status_dict,
                  **month_dict,
                  **week_dict,})


# ==============================================================================
# This is a model in case of using function based views:

# def activepage(request):
#     context_dict = {'nav_active':'active'}
#     return render(request, 'report/active.html',context=context_dict)
