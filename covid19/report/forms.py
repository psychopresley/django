from django import forms
from django.core import validators
from report.models import Country, CountryInfo

COUNTRIES = Country.objects.all()
COUNTRIES_LIST = [(x,x) for x in COUNTRIES];

class FormName(forms.Form):
    country= forms.CharField(label='Select country', label_suffix=': ',
                             widget=forms.Select(choices=COUNTRIES_LIST),
                             initial='Brazil');

    country.widget.attrs.update({'class': 'form-select-sm'})

    botcatcher = forms.CharField(required=False,
                                 widget=forms.HiddenInput,
                                 validators=[validators.MaxLengthValidator(0)]);
