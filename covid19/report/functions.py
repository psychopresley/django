import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE','covid19.settings')
django.setup()

import numpy as np
from datetime import datetime, timedelta
from report.models import ISOCodeData, UNData
from collections import OrderedDict
from sklearn.linear_model import LinearRegression, TheilSenRegressor, RANSACRegressor, HuberRegressor
from sklearn.metrics import mean_squared_error, r2_score

# Importing geoip2 and correlated modules:
from geoip2.database import Reader
from socket import gethostbyname, getfqdn
import requests

# Importing plotly modules:
import plotly.graph_objs as go
import plotly.express as px
from plotly.offline import plot
from plotly.subplots import make_subplots

# Importing fusioncharts.py module:
from . import fusioncharts as fsn


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
def quantiles_pos(arg,model_coef,x_values):
    for i in list(range(0,len(x_values)-1)):
        if x_values[i] <= arg < x_values[i+1]:
            line=model_coef[i]

    return line[0]*(arg - line[1]) + line[2]


# creating quartiles map function:
def quantiles_model(quantiles,end_of_scale=1):
    y=list(quantiles.keys())
    x=list(quantiles.values())

    model_coef=[]
    for i in list(range(1,len(x))):
        alpha = (y[i]-y[i-1])/(x[i]-x[i-1])
        model_coef.append((alpha,x[i-1],y[i-1]))

    model_coef.append((alpha,end_of_scale+1,1))

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

def quartiles_gauge(value,quartile,quartile_position,text='Indicator',suffix='%',precision=2):

    max_range = value/quartile_position
    if quartile[0] == '1':
        number_color = 'green'
        quartile_dict={'range': [0, 0.1*max_range], 'color': 'green'}
    elif quartile[0] == '2':
        number_color = 'blue'
        quartile_dict={'range': [0.1*max_range, 0.5*max_range], 'color': 'blue'}
    elif quartile[0] == '3':
        number_color = 'yellow'
        quartile_dict={'range': [0.5*max_range, 0.9*max_range], 'color': 'yellow'}
    else:
        number_color = 'red'
        quartile_dict={'range': [0.9*max_range, max_range], 'color': 'red'}


    # SPEEDOMETER:
    fig = go.Figure(go.Indicator(
    domain = {'row': 0, 'column': 0},
    mode = "gauge+number",
    value = value,
    delta = {'reference':0},
    title = {'text': text},
    number = {'suffix':suffix,'valueformat':',.{}f'.format(precision)},
    gauge = {
            'axis': {'range': [None, max_range], 'tickwidth': 1, 'tickcolor': "darkblue", 'showticklabels': False,},
            'bar': {'color': "black"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "purple",
            'steps': [quartile_dict],}))

    fig.add_trace(go.Indicator(
        mode = "number+delta",
        value = int(quartile[0]),
        delta = {'reference':int(quartile[0]) - quartile_position,'valueformat':'.1%'},
        number = {'font':{'color':number_color},'prefix':'Q'},
        domain = {'row': 1, 'column': 0}))

    fig.update_layout(
    grid = {'rows': 2, 'columns': 1, 'pattern': "independent"},
    template="seaborn",
    plot_bgcolor='white',
    )

    return plot({'data':fig,},output_type='div', include_plotlyjs=False, show_link=False, link_text="")

def top_ten_bar(database,column,title='My bar chart'):

    xdata=[]
    ydata=[]

    for obj in database:
        xdata.append(obj.__dict__[column])
        ydata.append(obj.__str__())

    fig = go.Figure()

    fig.update_layout(
    template="seaborn",
    plot_bgcolor='white',
    title = {'text':title,'font':{'family':'Quicksand','size':24,}},
    )

    # Add traces
    fig.add_trace(go.Bar(x=xdata[::-1],
                         y=ydata[::-1],
                         text=xdata[::-1],
                         textposition='auto',
                         marker={'color':xdata[::-1],'colorscale':'Bluered'},
                         orientation='h'))

    return plot({'data':fig,},output_type='div', include_plotlyjs=False, show_link=False, link_text="")

def scatter_undata(xdata,ydata,labels,xtext='xaxis',ytext='yaxis',with_fit=False,fit_intercept=True):

    fig = go.Figure()

    fig.update_layout(
    template="seaborn",
    plot_bgcolor='white',
    )

    fig.update_xaxes(title_text=xtext)
    fig.update_yaxes(title_text=ytext)

    # Add traces
    fig.add_trace(go.Scatter(x=xdata, y=ydata,mode='markers',name='countries',hovertext=labels))

    fit_parameters={}
    if with_fit:
        # SCIKIT-LEARN LINEAR REGRESSION MODELS:

        model = LinearRegression(fit_intercept=fit_intercept)
        model.fit(xdata.reshape(-1,1), ydata)

        ypred = model.predict(xdata.reshape(-1, 1))

        fit_parameters = {'coef':model.coef_,
                          'intercept': model.intercept_,
                          'r2':r2_score(ydata,ypred),
                          }

        # Add model traces
        fig.add_trace(go.Scatter(x=xdata, y=ypred,name='fit model'))
    else:
        pass

    plot_obj = plot({'data':fig,},output_type='div', include_plotlyjs=False, show_link=False, link_text="")
    plot_dict = {**fit_parameters,
                 'plot_obj':plot_obj,
                 }

    return plot_dict

def rank_bullets(value,range=[0,100],text='Bullets',suffix='°'):

    min_range = range[0]
    max_range = range[1]

    # BULLETS:
    fig = go.Figure()

    fig.add_trace(go.Indicator(
        mode = "number+gauge+delta",
        value = value,
        number = {'suffix':suffix},
        delta = {'reference': 0},
        domain = {'x': [0.25, 1], 'y': [0.08, 0.25]},
        title = {'text': text},
        gauge = {
            'shape': "bullet",
            'axis': {'range': [min_range, max_range]},
            'threshold': {
                'line': {'color': "black", 'width': 2},
                'thickness': 0.75,
                'value': value},
            'steps': [
                {'range': [min_range, max_range/2], 'color': "gray"},
                {'range': [max_range/2, max_range], 'color': "lightgray"}],
            'bar': {'color': "black"}}))

    fig.add_trace(go.Indicator(
        mode = "number+gauge+delta",
        value = value,
        number = {'suffix':suffix},
        delta = {'reference': 0},
        domain = {'x': [0.25, 1], 'y': [0.4, 0.6]},
        title = {'text': text},
        gauge = {
            'shape': "bullet",
            'axis': {'range': [min_range, max_range]},
            'threshold': {
                'line': {'color': "black", 'width': 2},
                'thickness': 0.75,
                'value': 170},
            'steps': [
                {'range': [min_range, max_range/2], 'color': "gray"},
                {'range': [max_range/2, max_range], 'color': "lightgray"}],
            'bar': {'color': "black"}}))

    fig.update_layout(height = 400 , margin = {'t':0, 'b':0, 'l':0}, template="seaborn", plot_bgcolor='white')

    return plot({'data':fig,},output_type='div', include_plotlyjs=False, show_link=False, link_text="")

def fusion_gauge(value, quartile, id):

    if quartile[0] == '1':
        number_color = 'green'
        quartile_dict={'range': [0, 10], 'color': 'green'}
        # quartile_dict={'range': [0, 0.4], 'color': 'green'}
        suffix='st'
    elif quartile[0] == '2':
        number_color = 'blue'
        quartile_dict={'range': [10, 50], 'color': 'blue'}
        # quartile_dict={'range': [0.4, 2], 'color': 'blue'}
        suffix='nd'
    elif quartile[0] == '3':
        number_color = 'yellow'
        quartile_dict={'range': [50, 90], 'color': 'yellow'}
        # quartile_dict={'range': [2, 3.6], 'color': 'yellow'}
        suffix='rd'
    else:
        number_color = 'red'
        quartile_dict={'range': [90, 100], 'color': 'red'}
        # quartile_dict={'range': [3.6, 4], 'color': 'red'}
        suffix='th'

    #Load dial indicator values from simple string array# e.g.dialValues = ["52", "10", "81", "95"]
    dialValues = ["{}".format(value)]

    # widget data is passed to the `dataSource` parameter, as dict, in the form of key-value pairs.
    dataSource = OrderedDict()

    # The `widgetConfig` dict contains key-value pairs of data for widget attribute
    widgetConfig = OrderedDict()
    widgetConfig["caption"] = id
    widgetConfig["lowerLimit"] = "0"
    widgetConfig["upperLimit"] = "4"
    widgetConfig["showValue"] = "1"
    # widgetConfig["numberSuffix"] = "%"
    widgetConfig["theme"] = "fusion"
    widgetConfig["showToolTip"] = "0"

    # The `colorData` dict contains key-value pairs of data for ColorRange of dial
    colorRangeData = OrderedDict()
    colorRangeData["color"] = [{
            "minValue": "0",
            "maxValue": "1",
            "code": "#198754"
        },
        {
            "minValue": "1",
            "maxValue": "5",
            "code": "#0d6efd"
        },
        {
            "minValue": "50",
            "maxValue": "90",
            "code": "#ffc107"
        },
        {
            "minValue": "90",
            "maxValue": "100",
            "code": "#dc3545"
        }

    ]

    # Convert the data in the `dialData` array into a format that can be consumed by FusionCharts.
    dialData = OrderedDict()
    dialData["dial"] = []

    dataSource["chart"] = widgetConfig
    dataSource["colorRange"] = colorRangeData
    dataSource["dials"] = dialData

    # Iterate through the data in `dialValues` and insert into the `dialData["dial"]` list.
    # The data for the `dial`should be in an array wherein each element of the
    # array is a JSON object# having the `value` as keys.
    for i in range(len(dialValues)):
        dialData["dial"].append({
        "value": dialValues[i]
    })
    # Create an object for the angular-gauge using the FusionCharts class constructor
    # The widget data is passed to the `dataSource` parameter.
    return fsn.FusionCharts("angulargauge", "{}".format(id), "100%", "200", "{}-container".format(id), "json", dataSource).render()
