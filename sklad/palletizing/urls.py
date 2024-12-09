from django.urls import path, include
from . import views


app_name = 'palletizing'


urlpatterns = [
    path('', views.mainPallet, name='mainPallet'),
    path('selectOrder/<str:arg>', views.selectLine, name='orderLine'),
    path('OrderBegin', views.startPalleting, name='startPalleting'),
]
