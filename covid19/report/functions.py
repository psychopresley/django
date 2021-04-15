import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE','covid19.settings')
django.setup()

import numpy as np
from datetime import datetime, timedelta
from report.models import ISOCodeData, UNData


# Importing geoip2 and correlated modules:
from geoip2.database import Reader
from socket import gethostbyname, getfqdn
import requests

# Importing plotly modules:
import plotly.graph_objs as go
import plotly.express as px
from plotly.offline import plot
from plotly.subplots import make_subplots


def db_del(database,confirm_before=True):
    # This function delete all entries in "database" model

    flag = True

    if confirm_before:
        confirm_delete = input('This will erase all entries in models.StatusReport. Press "n" if you wish to skip delete or any other key to continue: ')

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

def ordinal(x):
    # Function to be used in date format:
    if str(x)[-1] == '1':
        return 'st'
    elif str(x)[-1] == '2':
        return 'nd'
    elif str(x)[-1] == '3':
        return 'rd'
    else:
        return 'th'

# creating quartiles map function:
def quart_func(x,q,case):
    if x < q[1]:
        return '1st (very low {})'.format(case.lower())
    elif q[1] <= x < q[2]:
        return '2nd (medium-low {})'.format(case.lower())
    elif q[2] <= x < q[3]:
        return '3rd (medium-high {})'.format(case.lower())
    else:
        return '4th (very high {})'.format(case.lower())

# creating quartiles map function:
def quantiles_pos(mortality, model_coef):
    return ([mortality**4,mortality**3,mortality**2,mortality,1]*model_coef).item()

# creating quartiles map function:
def quantiles_model(quantiles):
    regressors = []
    y=[]
    for k,v in quantiles.items():
        regressors.append([v**4,v**3,v**2,v,1])
        y.append([k])

    regressors = np.matrix(regressors)
    model_coef = np.linalg.inv(regressors)*np.array(y)

    return model_coef

def population(x):
    exception_list = ['Cruise Ship','Taiwan']
    if x in exception_list:
        population=1e10
    else:
        x = ISOCodeData.objects.get(country_name=x)
        x = UNData.objects.get(country=x.un_name)
        population = x.population

    return population


# defining custom function to obtain first and last day of the week:
def start_end_week(year, week):
    monday = datetime.strptime(f'{year}-{week}-1', "%Y-%W-%w").date()
    return '{} / {}'.format(monday.strftime('%b, %d'), (monday + timedelta(days=6.9)).strftime('%b, %d'))


# defining custom function to obtain the public IP address of the request:
def getIP(reader):
    '''
    The code below was taken from:
    https://stackoverflow.com/questions/2311510/getting-a-machines-external-ip-address-with-python/41432835

    Please refer to the link for original code and credits.

    geoip2 api documentation: https://geoip2.readthedocs.io/en/latest/
    maxmind database: https://www.maxmind.com
    '''
    # local_ip = gethostbyname(getfqdn())
    public_ip = requests.get('https://www.wikipedia.org').headers['X-Client-IP']
    response = reader.country(public_ip)

    return response.country


def month_subplot(subplot1data,subplot2data,labels):
    # 1 - MONTH REPORT CHARTS:
    fig = make_subplots(
    rows=2, cols=1,
    row_heights=[0.5, 0.5],
    # subplot_titles=("Confirmed","Deaths"),
    shared_xaxes=True,
    specs=[[{"type": "bar"}],
           [{"type": "bar"}]])

    fig.add_trace(
    go.Bar(x=subplot1data[0], y=subplot1data[1], name=labels[0], opacity=0.5, marker={"color":subplot1data[1][::-1],"colorscale":'algae',"reversescale":True},showlegend=False,),
    row=1, col=1
    )

    fig.add_trace(
    go.Bar(x=subplot2data[0], y=subplot2data[1], name=labels[1], opacity=0.5, marker={"color":subplot2data[1][::-1],"colorscale":'Teal',"reversescale":True},showlegend=False,),
    row=2, col=1
    )

    fig.update_layout(
    template="seaborn",
    margin={'l':20,'r':10,'t':30,'b':10},
    plot_bgcolor='white',
    font_family='Quicksand',
    )

    # Update xaxis properties
    fig.update_xaxes(title_text="Month", row=2, col=1, type='category')
    fig.update_xaxes(row=1, col=1, type='category')

    # Update Y-axis properties
    fig.update_yaxes(title_text=labels[0], row=1, col=1)
    fig.update_yaxes(title_text=labels[1], row=2, col=1)

    return plot({'data':fig,},output_type='div', include_plotlyjs=False, show_link=False, link_text="")


def week_subplot(subplot1data,subplot2data,labels):
    # 2 - WEEK REPORT CHARTS:
    fig = make_subplots(
    rows=2, cols=1,
    row_heights=[0.5, 0.5],
    # subplot_titles=("Confirmed","Deaths"),
    shared_xaxes=True,
    specs=[[{"type": "bar"}],
           [{"type": "bar"}]])

    fig.update_layout(
    template="seaborn",
    margin={'l':20,'r':10,'t':30,'b':10},
    plot_bgcolor='white',
    font_family="Quicksand",
    )

    fig.append_trace(
    go.Bar(x=subplot1data[0], y=subplot1data[1], name=labels[0], opacity=0.5, marker={"color":subplot1data[1][::-1],"colorscale":'algae',"reversescale":True},showlegend=False,),
    row=1, col=1
    )

    fig.append_trace(
    go.Bar(x=subplot2data[0], y=subplot2data[1], name=labels[1], opacity=0.5, marker={"color":subplot2data[1][::-1],"colorscale":'Teal',"reversescale":True},showlegend=False,),
    row=2, col=1
    )

    # Update X-axis properties
    fig.update_xaxes(title_text="Week", row=2, col=1, type='category')
    fig.update_xaxes(row=1, col=1, type='category')

    # Update Y-axis properties
    fig.update_yaxes(title_text=labels[0], row=1, col=1)
    fig.update_yaxes(title_text=labels[1], row=2, col=1)

    return plot({'data':fig,},output_type='div', include_plotlyjs=False, show_link=False, link_text="")

def heatmap_subplot(subplot1data,subplot2data,labels):
    # Heatmaps
    fig = make_subplots(
    rows=2, cols=1,
    row_heights=[0.5, 0.5],
    shared_xaxes=True,
    specs=[[{"type": "heatmap"}],
           [{"type": "heatmap"}]])

    fig.update_layout(
    template="seaborn",
    margin={'l':20,'r':10,'t':30,'b':10},
    plot_bgcolor='white',
    font_family="Quicksand",
    )

    fig.append_trace(
    go.Heatmap(
        z=[subplot2data[1]],
        x=subplot2data[0],
        y=[labels[1]],
        colorscale='RdBu_r',
        showscale=False,
        ),row=2, col=1)

    fig.append_trace(
    go.Heatmap(
        z=[subplot1data[1]],
        x=subplot1data[0],
        y=[labels[0]],
        colorscale='RdBu_r',
        showscale=False,
        ),row=1, col=1)


    # Update X-axis properties
    fig.update_xaxes(title_text="Week", row=2, col=1, type='category')
    fig.update_xaxes(row=1, col=1, type='category')

    return plot({'data':fig,},output_type='div', include_plotlyjs=False, show_link=False, link_text="")

def density_plot(x,y):
    # CONTOUR MAPS:
    fig = go.Figure(go.Histogram2dContour(
        x=x,
        y=y,
        colorscale='RdBu_r',
        histnorm="percent",
        xbins={'end':max(x)},
        ybins={'end':max(y)},
        showscale=False,
        ncontours=20,
        contours={'showlines':False}
    ))

    fig.update_layout(
    template="seaborn",
    plot_bgcolor='white',
    title={'text':"Density levels",'font':{'family':'Quicksand','size':30}},
    )

    return plot({'data':fig,},output_type='div', include_plotlyjs=False, show_link=False, link_text="")
