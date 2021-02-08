from django.shortcuts import render
from . import forms

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
            print(selected_country);

            return render(request, 'report/country_assessment.html',
                          {'form':form,'country_content':selected_country})

    return render(request, 'report/country_assessment.html', {'form':form,'country_content':'Brazil'})

def deathpage(request):
    return render(request, 'report/death_cases.html')

def readpage(request):
    return render(request, 'report/read_me.html')

def worldpage(request):
    return render(request, 'report/world_data.html')
