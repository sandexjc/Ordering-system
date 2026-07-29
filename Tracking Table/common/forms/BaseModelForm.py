from django import forms
from common.mixins import FormFieldsStyleMixin

class BaseModelForm(FormFieldsStyleMixin, forms.ModelForm):

    """

    Hierarchy:
    FormFieldsStyleMixin -> BaseModelForm
    forms.ModelForm -> BaseModelForm

    --- Fields inherited from FormFieldsStyleMixin ---

    No explicit class fields inherited.

    --- Fields inherited from forms.ModelForm ---

    No explicit class fields inherited.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap_styling()

    class Meta:
        abstract = True