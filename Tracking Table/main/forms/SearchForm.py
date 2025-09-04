from common.forms import BaseForm
from django import forms

class SearchForm(BaseForm):

    category_choices = [
        ('All', 'All'),
        ('ID', 'ID'),
        ('Client Name', 'Client Name'),
        ('Telephone', 'Telephone'),
        ('Date', 'Date')
    ]

    category = forms.ChoiceField(choices=category_choices)
    search_field = forms.CharField(max_length=100, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['search_field'].label = ""
        self.fields['search_field'].widget.attrs['placeholder'] = 'Search here...'
        self.fields['category'].widget.attrs = {
            'class': 'form-select',
        }