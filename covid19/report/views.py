from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View,TemplateView
from . import forms
from report.models import Country,StatusReport

# Create your views here.

# THIS IS THE HOME (INDEX) PAGE:

class IndexView(TemplateView):
    template_name = 'report/index.html'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)

        context['nav_index'] = 'active'
        context['report_date'] = StatusReport.objects.get(country__name='Brazil').date

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

    country = Country.objects.get(name=selected_country)
    status = StatusReport.objects.get(country__name=selected_country).__dict__


    # PASSING COUNTRYINFO MODEL VARIABLES AS TEMPLATE TAGS
    country_dict = {'country_name':selected_country,
                    'country_coord':country._coordinates_(),}

    for k,v in country.__dict__.items():
        country_dict = {**country_dict,**{k:country.__dict__[k]}}


    # PASSING STATUSREPORT MODEL VARIABLES AS TEMPLATE TAGS
    status_dict = {'active_pct':status['active']/status['confirmed'],
                   'mortality':status['deaths']/status['confirmed'],}

    for k,v in status.items():
        status_dict = {**status_dict,**{k:status[k]}}


    return render(request,'report/countries.html',
                  {'form':form,'nav_countries':'active',**country_dict,**status_dict})


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
