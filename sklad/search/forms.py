from .models import Search
from django.forms import ModelForm, TextInput


class SearchForm(ModelForm):
    class Meta:
        model = Search
        fields = ['searchField']

        widgets = {
            "searchField": TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Поиск',
                'autofocus': 'true'
            })
        }
