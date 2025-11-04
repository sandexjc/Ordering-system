from django import forms
from common.mixins import FieldsStyleMixin

class BaseForm(FieldsStyleMixin, forms.Form):

    """ Top level base form for all non-model forms. """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap_styling()