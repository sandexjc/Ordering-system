from django import forms
from common.mixins import FieldStyleMixin

class BaseModelForm(FieldStyleMixin, forms.ModelForm):
    
    """ Top level model form for the whole project. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap_styling()

    class Meta:
        abstract = True