from common.forms import BaseForm
from django import forms

class FilterForm(BaseForm):

    """

    Hierarchy:
    FormFieldsStyleMixin -> BaseForm -> FilterForm
    forms.Form -> BaseForm -> FilterForm

    --- Fields inherited from BaseForm ---

    No explicit class fields inherited.

    """

    fast_select_choice = [
        (100, 'последни 100'),
        (200, 'последни 200'),
        (300, 'последни 300'),
        (500, 'последни 500'),
        ('all', 'всички'),
    ]

    fast_select = forms.ChoiceField(
        widget = forms.RadioSelect, 
        choices = fast_select_choice, 
        initial = '100'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fast_select'].label = "Виж"
        self.fields['fast_select'].widget.attrs = {
            'class': 'form-check',
        }