from .models import PalletCode
from django.forms import ModelForm, TextInput


class SearchForm(ModelForm):
    class Meta:
        model = PalletCode
        fields = ['palletField']

        widgets = {
            "palletField": TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Код паллета'
            })
        }
