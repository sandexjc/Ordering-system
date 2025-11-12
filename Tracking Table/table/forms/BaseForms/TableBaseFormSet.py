from django import forms
from common.mixins import FormSetStyleMixin

class TableFormSet(FormSetStyleMixin, forms.BaseInlineFormSet):
    
    """ Intermediate domain level base inline formset with styled deletion widget. """
    
    pass