from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View,TemplateView
from . import forms
from report.models import StatusReport, MonthReport, WeekReport

# Importing plotly modules:
import plotly.graph_objs as go
import plotly.express as px
from plotly.offline import plot
from plotly.subplots import make_subplots

# Importing python native modules:
from calendar import week
from datetime import datetime, timedelta

# defining custom function to obtain first and last day of the week:
def start_end_week(year, week):
    monday = datetime.strptime(f'{year}-{week}-1', "%Y-%W-%w").date()
    return '{} / {}'.format(monday.strftime('%b, %d'), (monday + timedelta(days=6.9)).strftime('%b, %d'))

# Create your views here.

# THIS IS THE HOME (INDEX) PAGE:

class IndexView(TemplateView):
    template_name = 'report/index.html'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)

        form = forms.SelectCountry()
        selected_country = form['country'].initial

        context['nav_index'] = 'navbar-item-active'
        context['report_date'] = StatusReport.objects.order_by('-date')[0].date
        context['form'] = form

        return context


# THESE ARE THE OTHER PAGES:
class ActiveView(TemplateView):
    template_name = 'report/active.html'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['nav_active'] = 'navbar-item-active'

        form = forms.SelectCountry()
        selected_country = form['country'].initial
        context['form'] = form

        return context


class ConfirmedView(TemplateView):
    template_name = 'report/confirmed.html'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['nav_confirmed'] = 'navbar-item-active'

        form = forms.SelectCountry()
        selected_country = form['country'].initial
        context['form'] = form

        return context


def countriespage(request): # This is a FORM PAGE
    form = forms.SelectCountry()
    selected_country = form['country'].initial

    if request.method == 'POST':
        form = forms.SelectCountry(request.POST);

        if form.is_valid():
            selected_country = form.cleaned_data['country'];

    status = StatusReport.objects.get(country=selected_country)
    month_report = MonthReport.objects.filter(country=selected_country).order_by('-month')
    week_report = WeekReport.objects.filter(country=selected_country).order_by('-week')

    # PASSING STATUSREPORT MODEL VARIABLES AS TEMPLATE TAGS
    status_dict = {'country_coord':status.country._coordinates_(),
                   'report_date': status.date,
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


    # 1 - MONTH REPORT CHARTS:
    fig = make_subplots(
    rows=2, cols=1,
    row_heights=[0.5, 0.5],
    # subplot_titles=("Confirmed","Deaths"),
    shared_xaxes=True,
    specs=[[{"type": "bar"}],
           [{"type": "bar"}]])

    fig.add_trace(
    go.Bar(x=x_month[::-1], y=y_confirmed[::-1], name='Confirmed', opacity=0.5, marker={"color":y_confirmed,"colorscale":'algae',"reversescale":True},showlegend=False,),
    row=1, col=1
    )

    fig.add_trace(
    go.Bar(x=x_month[::-1], y=y_deaths[::-1], name='Deaths', opacity=0.5, marker={"color":y_deaths,"colorscale":'Teal',"reversescale":True},showlegend=False,),
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
    fig.update_yaxes(title_text="Confirmed", row=1, col=1)
    fig.update_yaxes(title_text="Deaths", row=2, col=1)

    plot_month = plot({'data':fig,},output_type='div', include_plotlyjs=False, show_link=False, link_text="")


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
    go.Bar(x=x_week[::-1], y=y_confirmed_week[::-1], name='Confirmed', opacity=0.5, marker={"color":y_confirmed_week,"colorscale":'algae',"reversescale":True},showlegend=False,),
    row=1, col=1
    )

    fig.append_trace(
    go.Bar(x=x_week[::-1], y=y_deaths_week[::-1], name='Deaths', opacity=0.5, marker={"color":y_deaths_week,"colorscale":'Teal',"reversescale":True},showlegend=False,),
    row=2, col=1
    )


    # Update X-axis properties
    fig.update_xaxes(title_text="Week", row=2, col=1, type='category')
    fig.update_xaxes(row=1, col=1, type='category')

    # Update Y-axis properties
    fig.update_yaxes(title_text="Confirmed", row=1, col=1)
    fig.update_yaxes(title_text="Deaths", row=2, col=1)

    plot_week = plot({'data':fig,},output_type='div', include_plotlyjs=False, show_link=False, link_text="")

    return render(request,'report/countries.html',
                  {'form':form,
                  'nav_countries':'navbar-item-active',
                  'plot_month':plot_month,
                  'plot_week':plot_week,
                  **status_dict,
                  **month_dict,
                  **week_dict,})


class DeathsView(TemplateView):
    template_name = 'report/deaths.html'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['nav_deaths'] = 'navbar-item-active'

        form = forms.SelectCountry()
        selected_country = form['country'].initial
        context['form'] = form

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


# ==============================================================================
# This is a model in case of using function based views:

# def activepage(request):
#     context_dict = {'nav_active':'active'}
#     return render(request, 'report/active.html',context=context_dict)
