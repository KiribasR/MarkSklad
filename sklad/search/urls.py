from django.urls import path, include
from . import views


app_name = 'search'

urlpatterns = [
    path('', views.search, name='search'),
    path('searchresult', views.search_results, name='searchresult'),
]