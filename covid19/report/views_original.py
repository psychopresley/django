from django.shortcuts import render
from . import forms
from report.models import Country, CountryInfo, StatusReport

# Create your views here.
# THIS IS THE INITIAL (INDEX) PAGE:

def index(request):
    status_date = StatusReport.objects.get(country__name='Brazil').date

    context_dict = {'nav_index':'active','report_date':status_date,}
    return render(request, 'report/index.html',context=context_dict)

# THESE ARE THE OTHER PAGES:

def activepage(request):
    context_dict = {'nav_active':'active'}
    return render(request, 'report/active_cases.html',context=context_dict)

def confirmedpage(request):
    context_dict = {'nav_confirmed':'active'}
    return render(request, 'report/confirmed_cases.html',context=context_dict)

def countriespage(request): # This is a FORM PAGE
    form = forms.FormName()
    selected_country = form['country'].initial

    if request.method == 'POST':
        form = forms.FormName(request.POST);

        if form.is_valid():
            selected_country = form.cleaned_data['country'];

    country = CountryInfo.objects.get(country__name=selected_country)
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


    return render(request,'report/country_assessment.html',
                  {'form':form,'nav_countries':'active',**country_dict,**status_dict})

def deathpage(request):
    context_dict = {'nav_deaths':'active'}
    return render(request, 'report/death_cases.html',context=context_dict)

def readpage(request):
    context_dict = {'nav_readme':'active'}
    return render(request, 'report/read_me.html',context=context_dict)

def worldpage(request):
    return render(request, 'report/world_data.html')
