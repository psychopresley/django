from django import forms
from django.core import validators

COUNTRIES = ['Brazil','US','Canada','Japan','Sweden','Argentina'];
COUNTRIES_LIST = [(x,x) for x in COUNTRIES];

class FormName(forms.Form):
    country= forms.CharField(label='Select country', label_suffix=': ',
                             widget=forms.Select(choices=COUNTRIES_LIST));
    botcatcher = forms.CharField(required=False,
                                 widget=forms.HiddenInput,
                                 validators=[validators.MaxLengthValidator(0)]);
