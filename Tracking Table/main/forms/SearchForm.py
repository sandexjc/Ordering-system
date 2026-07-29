from common.forms import BaseForm
from django import forms

class SearchForm(BaseForm):

    """

    Hierarchy:
    FormFieldsStyleMixin -> BaseForm -> SearchForm
    forms.Form -> BaseForm -> SearchForm

    --- Fields inherited from BaseForm ---

    No explicit class fields inherited.

    """

    category_choices = [
        ('All', 'All'),
        ('ID', 'ID'),
        ('Client Name', 'Client Name'),
        ('Telephone', 'Telephone'),
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