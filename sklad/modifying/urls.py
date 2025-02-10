from django.urls import path, include
from . import views


app_name = 'modifying'


urlpatterns = [
    path('', views.mainModify, name='mainModify'),
    path('select', views.actionPallet, name='select'),
    path('action', views.actionModify, name='action'),
]
