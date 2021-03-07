from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View,TemplateView
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

    # PASSING STATUSREPORT MODEL VARIABLES AS TEMPLATE TAGS
    status = StatusReport.objects.get(country=selected_country)
    status_dict = {'country_coord':status.country._coordinates_(),
                   **status.country.__dict__,
                  }

    for k,v in status.__dict__.items():
        status_dict = {**status_dict,**{k:status.__dict__[k]}}


    # PASSING MONTHREPORT MODEL VARIABLES AS TEMPLATE TAGS
    def build_month_dict(obj,dict):
        return_dict={}
        for key in dict.keys():
            return_dict[key]=obj.__dict__[key.replace('_month','')]

        return return_dict

    month_report = MonthReport.objects.filter(country=selected_country).order_by('-month')
    month_report_dict = {
                         'month':[],
                         'confirmed_month':[],'confirmed_pct_change_month':[],
                         'confirmed_rank_region_month':[],'confirmed_rank_world_month':[],
                         'deaths_month':[],'deaths_pct_change_month':[],
                         'deaths_rank_region_month':[],'deaths_rank_world_month':[],
                        }

    rows=[]
    # for obj in month_report:
    #     dict = build_month_dict(obj,month_report_dict)
    #     rows.append(dict)

    for obj in month_report:
        dict={}
        for key in month_report_dict.keys():
            dict[key]=obj.__dict__[key.replace('_month','')]
        rows.append(dict)

    month_dict = {'month_rows':rows,'month_header':['','Confirmed','Rank (Region - World)','Deaths','Rank (Region - World)']}

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
