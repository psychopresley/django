from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View,TemplateView
from . import forms
from report.models import StatusReport, MonthReport

# Importing plotly modules:
import plotly.graph_objs as go
import plotly.express as px
from plotly.offline import plot
from plotly.subplots import make_subplots

# Create your views here.

# THIS IS THE HOME (INDEX) PAGE:

class IndexView(TemplateView):
    template_name = 'report/index.html'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)

        form = forms.SelectCountry()
        selected_country = form['country'].initial

        context['nav_index'] = 'active'
        context['report_date'] = StatusReport.objects.order_by('-date')[0].date
        context['form'] = form

        return context


# THESE ARE THE OTHER PAGES:
class ActiveView(TemplateView):
    template_name = 'report/active.html'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['nav_active'] = 'active'

        form = forms.SelectCountry()
        selected_country = form['country'].initial
        context['form'] = form

        return context


class ConfirmedView(TemplateView):
    template_name = 'report/confirmed.html'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['nav_confirmed'] = 'active'

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

    # ADDING SOME CHARTS:
    # Here's a nice page if you wish to know more about plotly + django:
    # https://www.codingwithricky.com/2019/08/28/easy-django-plotly/
    # colorscales code: https://plotly.com/python/builtin-colorscales/

    fig = make_subplots(
    rows=2, cols=1,
    row_heights=[0.5, 0.5],
    subplot_titles=("Confirmed","Deaths"),
    shared_xaxes=True,
    specs=[[{"type": "bar"}],
           [{"type": "bar"}]])

    fig.add_trace(
    go.Bar(x=x_month, y=y_confirmed, name='Confirmed', opacity=0.5, marker={"color":y_confirmed,"colorscale":'algae'},showlegend=False,),
    row=1, col=1
    )

    fig.add_trace(
    go.Bar(x=x_month, y=y_deaths, name='Deaths', opacity=0.5, marker={"color":y_deaths,"colorscale":'Teal'},showlegend=False,),
    row=2, col=1
    )

    fig.update_layout(
    template="seaborn",
    margin={'l':20,'r':10,'t':30,'b':10},
    plot_bgcolor='white',
    )

    # Update xaxis properties
    fig.update_xaxes(title_text="Month", row=2, col=1)

    plot_month = plot({'data':fig,},output_type='div', include_plotlyjs=False, show_link=False, link_text="")

    return render(request,'report/countries.html',
                  {'form':form,'nav_countries':'active','plot_month':plot_month,**status_dict,**month_dict})


class DeathsView(TemplateView):
    template_name = 'report/deaths.html'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['nav_deaths'] = 'active'

        form = forms.SelectCountry()
        selected_country = form['country'].initial
        context['form'] = form

        return context


class ReadMeView(TemplateView):
    template_name = 'report/read_me.html'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['nav_readme'] = 'active'

        form = forms.SelectCountry()
        selected_country = form['country'].initial
        context['form'] = form

        return context


# ==============================================================================
# This is a model in case of using function based views:

# def activepage(request):
#     context_dict = {'nav_active':'active'}
#     return render(request, 'report/active.html',context=context_dict)
