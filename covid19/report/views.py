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
    status = StatusReport.objects.get(country__name=selected_country)

    country_dict = {
                    'country_name':selected_country,
                    'country_coord':country._coordinates_(),
                    'country_region':country.region,
                    'internet_code':country.internet_code,
                    'map_image':country.map_image,
                    }

    status_dict = {
                    'confirmed_cases': '{:,}'.format(status.confirmed),
                    'confirmed_cases_world_rank': status.confirmed_rank_world,
                    'confirmed_cases_region_rank': status.confirmed_rank_region,
                    'new_confirmed_cases': '{:,}'.format(status.confirmed_new),
                    'new_confirmed_rank_region': '{:,}'.format(status.confirmed_new_rank_region),
                    'new_confirmed_rank_world': '{:,}'.format(status.confirmed_new_rank_world),
                    'confirmed_pct_change': '%.2f' % status.confirmed_pct_change,
                    'death_cases': '{:,}'.format(status.deaths),
                    'death_cases_world_rank': status.deaths_rank_world,
                    'death_cases_region_rank': status.deaths_rank_region,
                    'death_rate': "%.2f" % (status.deaths/status.confirmed*100),
                    'new_death_cases': '{:,}'.format(status.deaths_new),
                    'death_pct_change': '%.2f' % status.deaths_pct_change,
                    'active_cases': '{:,}'.format(status.active),
                    'active_pct': '%.2f%%' % (status.active/status.confirmed*100),
                    'new_active_cases': '{:,}'.format(status.active_new),
                    'active_cases_world_rank': status.active_rank_world,
                    'active_cases_region_rank': status.active_rank_region,
                    'report_date': status.date,
                    }

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
