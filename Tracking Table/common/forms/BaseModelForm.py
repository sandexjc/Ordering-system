from django import forms
from common.mixins import FormFieldsStyleMixin

class BaseModelForm(FormFieldsStyleMixin, forms.ModelForm):
    
    """ Top level model form for the whole project. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap_styling()

    class Meta:
        abstract = True