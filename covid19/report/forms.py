from django import forms
from django.core import validators
from report.models import Country

COUNTRIES = Country.objects.all()
COUNTRIES_LIST = list([(x.name,x.name) for x in COUNTRIES]);
COUNTRIES_LIST.sort()

class SelectCountry(forms.Form):
    country= forms.CharField(label='', label_suffix=': ',
                             widget=forms.Select(choices=COUNTRIES_LIST),
                             initial='Brazil');

    country.widget.attrs.update({'class': 'form-select-country'})

    botcatcher = forms.CharField(required=False,
                                 widget=forms.HiddenInput,
                                 validators=[validators.MaxLengthValidator(0)]);


# class SelectCountryModel(forms.ModelForm):
#     class Meta:
#         model = Country
#         fields='__all__'
