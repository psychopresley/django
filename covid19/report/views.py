from django.shortcuts import render
from . import forms
from report.models import Country, CountryInfo, StatusReport

# Create your views here.
# THIS IS THE INITIAL (INDEX) PAGE:

def index(request):
    status_date = StatusReport.objects.get(country__name='Brazil').__dict__['date']

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

    country_info = CountryInfo.objects.get(country__name=selected_country)
    status_info = StatusReport.objects.get(country__name=selected_country).__dict__

    country_dict = {
                    'country_name':selected_country,
                    'country_coord':country_info._coordinates_(),
                    'country_region':country_info.__dict__['region'],
                    'internet_code':country_info.__dict__['internet_code'],
                    'map_image':country_info.__dict__['map_image'],
                    }

    status_dict = {
                    'confirmed_cases': '{:,}'.format(status_info['confirmed']),
                    'confirmed_cases_world_rank': status_info['confirmed_rank_world'],
                    'confirmed_cases_region_rank': status_info['confirmed_rank_region'],
                    'new_confirmed_cases': '{:,}'.format(status_info['confirmed_new']),
                    'new_confirmed_rank_region': '{:,}'.format(status_info['confirmed_new_rank_region']),
                    'new_confirmed_rank_world': '{:,}'.format(status_info['confirmed_new_rank_world']),
                    'confirmed_pct_change': '%.2f' % status_info['confirmed_pct_change'],
                    'death_cases': '{:,}'.format(status_info['deaths']),
                    'death_cases_world_rank': status_info['deaths_rank_world'],
                    'death_cases_region_rank': status_info['deaths_rank_region'],
                    'death_rate': "%.2f" % (status_info['deaths']/status_info['confirmed']*100),
                    'new_death_cases': '{:,}'.format(status_info['deaths_new']),
                    'death_pct_change': '%.2f' % status_info['deaths_pct_change'],
                    'active_cases': '{:,}'.format(status_info['active']),
                    'active_pct': '%.2f%%' % (status_info['active']/status_info['confirmed']*100),
                    'new_active_cases': '{:,}'.format(status_info['active_new']),
                    'active_cases_world_rank': status_info['active_rank_world'],
                    'active_cases_region_rank': status_info['active_rank_region'],
                    'report_date': status_info['date'],
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
