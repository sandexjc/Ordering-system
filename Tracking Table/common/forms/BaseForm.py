from django import forms
from common.mixins import FieldStyleMixin

class BaseForm(FieldStyleMixin, forms.Form):

    """ Top level base form for all non-model forms. """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap_styling()