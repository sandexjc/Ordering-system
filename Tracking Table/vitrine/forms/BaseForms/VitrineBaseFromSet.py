from django import forms
from common.mixins import FormSetStyleMixin

class VitrineFormSet(FormSetStyleMixin, forms.BaseInlineFormSet):
    
    """ Intermediate vitrine app level base inline formset. """
    
    pass