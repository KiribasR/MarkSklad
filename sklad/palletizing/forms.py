from .models import *
from django.forms import ModelForm, TextInput


class PalletForm(ModelForm):
    class Meta:
        model = PalletCode
        fields = ['palletField']

        widgets = {
            "palletField": TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Код паллета'
            })
        }


class AggregateForm(ModelForm):
    class Meta:
        model = AggregateCode
        fields = ['aggregateField']

        widgets = {
            "aggregateField": TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Отсканируйте код агрегата'
            })
        }
