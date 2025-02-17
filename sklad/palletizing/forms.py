from .models import *
from django.forms import ModelForm, TextInput, Form


class PalletTaskForm(ModelForm):
    class Meta:
        model = PalletTask
        fields = ['taskField']

        widgets = {
            "taskField": forms.Textarea(attrs={
                'readonly': 'true',
                'rows': '1',
                'cols': '30'
            })
        }


class PalletForm(ModelForm):
    class Meta:
        model = PalletCode
        fields = ['palletField', 'taskField', 'curPallet']

        widgets = {
            "palletField": TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Код паллета',
                'autofocus': 'true'
            }),
            "taskField": forms.Textarea(attrs={
                    'readonly': 'true',
                    'rows': '1',
                    
             }),
            "curPallet": forms.Textarea(attrs={
                    'readonly': 'true',
                    'rows': '1',
             })
        }


"""class AggCodeForm(forms.Form):
    aggregateField = forms.CharField(widget=TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Отсканируйте код агрегата',
                'autofocus': 'true'}))

    pallet = forms.CharField(widget=TextInput(attrs={

                'readonly': True
            }))"""


class AggregateForm(ModelForm):
    class Meta:
        model = AggregateCode
        fields = ['aggregateField', 'pallet', 'task']

        widgets = {
            "aggregateField": TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Отсканируйте код агрегата',
                'autofocus': 'true'
            }),
            "pallet": forms.Textarea(attrs={
                'readonly': 'true',
                    'rows': '1'
                
            }),
            "task": forms.Textarea(attrs={
                'readonly': 'true',
                    'rows': '1'
        })
        }
