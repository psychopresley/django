"""covid19 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from report import views

app_name = 'report'

urlpatterns = [
    path('active_cases/', views.activepage, name='activepage'),
    path('confirmed_cases/', views.confirmedpage, name='confirmedpage'),
    path('death_cases/', views.deathpage, name='deathpage'),
    path('read_me/', views.readpage, name='readpage'),
    path('word_data/', views.worldpage, name='worldpage'),
    path('countries/', views.countriespage, name='countriespage'),
]
