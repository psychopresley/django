from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View,TemplateView
from calendar import monthrange
from . import forms
from report.models import StatusReport, MonthReport

# Create your views here.

# THIS IS THE HOME (INDEX) PAGE:

class IndexView(TemplateView):
    template_name = 'report/index.html'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)

        context['nav_index'] = 'active'
        context['report_date'] = StatusReport.objects.order_by('-date')[0].date

        return context


# THESE ARE THE OTHER PAGES:
class ActiveView(TemplateView):
    template_name = 'report/active.html'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['nav_active'] = 'active'

        return context


class ConfirmedView(TemplateView):
    template_name = 'report/confirmed.html'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['nav_confirmed'] = 'active'

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
                         'month':[],
                         'confirmed_month':[],'confirmed_pct_change_month':[],
                         'confirmed_rank_region_month':[],'confirmed_rank_world_month':[],
                         'deaths_month':[],'deaths_pct_change_month':[],
                         'deaths_rank_region_month':[],'deaths_rank_world_month':[],
                        }

    rows=[]
    idx=0
    for obj in month_report:
        dict={}
        for key in month_report_dict.keys():
            dict[key]=obj.__dict__[key.replace('_month','')]
        dict = {**dict,**{'idx':idx,}}
        idx += 1

        rows.append(dict)

    days_in_month = monthrange(status.date.year,status.date.month)[1]

    deaths_prediction = int(month_report[0].deaths*(days_in_month)/status.date.day)
    confirmed_prediction = int(month_report[0].confirmed*(days_in_month)/status.date.day)

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

    return render(request,'report/countries.html',
                  {'form':form,'nav_countries':'active',**status_dict,**month_dict})


class DeathsView(TemplateView):
    template_name = 'report/deaths.html'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['nav_deaths'] = 'active'

        return context


class ReadMeView(TemplateView):
    template_name = 'report/read_me.html'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['nav_readme'] = 'active'

        return context


# ==============================================================================
# This is a model in case of using function based views:

# def activepage(request):
#     context_dict = {'nav_active':'active'}
#     return render(request, 'report/active.html',context=context_dict)
