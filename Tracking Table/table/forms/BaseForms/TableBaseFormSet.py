from django import forms
from common.mixins import FormSetStyleMixin

class TableFormSet(FormSetStyleMixin, forms.BaseInlineFormSet):
    
    """ Intermediate table app level base inline formset. """
    
    pass