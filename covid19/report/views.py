from django.shortcuts import render
from . import forms
from report.models import Country, CountryInfo

# Create your views here.
# THIS IS THE INITIAL (INDEX) PAGE:

def index(request):
    return render(request, 'report/index.html')

# THESE ARE THE OTHER PAGES:

def activepage(request):
    return render(request, 'report/active_cases.html')

def confirmedpage(request):
    return render(request, 'report/confirmed_cases.html')

def countriespage(request): # This is a FORM PAGE
    form = forms.FormName()

    if request.method == 'POST':
        form = forms.FormName(request.POST);

        if form.is_valid():
            selected_country = form.cleaned_data['country'];
            country_info = CountryInfo.objects.get(country__name=selected_country)

            country_dict = {
                            'country_name':selected_country,
                            'country_coord':country_info._coordinates_(),
                            'country_region':country_info._region_(),
                            }

            return render(request,'report/country_assessment.html',
                          {'form':form,**country_dict})

    return render(request, 'report/country_assessment.html', {'form':form,'country_name':'Brazil'})

def deathpage(request):
    return render(request, 'report/death_cases.html')

def readpage(request):
    return render(request, 'report/read_me.html')

def worldpage(request):
    return render(request, 'report/world_data.html')
