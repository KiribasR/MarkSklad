from django.urls import path, include
from . import views


app_name = 'palletizing'


urlpatterns = [
    path('', views.mainPallet, name='mainPallet'),
    path('selectOrder/<str:arg>', views.selectLine, name='orderLine'),
    path('OrderBegin/<str:batch>', views.startPalleting, name='startPalleting'),
    path('palletField', views.addPalletNumber, name='palletField'),
    path('newPalletField', views.newPalletSetting, name='newPalletField'),
    path('aggregateField', views.addAggregateNumber, name='aggregateField'),
    #path('confirmPallet', views.confirmPallet, name='confirmPallet'),
    path('closePallet', views.closePallet, name='closePallet'),
]
