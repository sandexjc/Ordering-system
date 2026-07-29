from django import forms
from common.mixins import FormFieldsStyleMixin

class BaseForm(FormFieldsStyleMixin, forms.Form):

    """

    Hierarchy:
    FormFieldsStyleMixin -> BaseForm
    forms.Form -> BaseForm

    --- Fields inherited from FormFieldsStyleMixin ---

    No explicit class fields inherited.

    --- Fields inherited from forms.Form ---

    No explicit class fields inherited.

    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap_styling()