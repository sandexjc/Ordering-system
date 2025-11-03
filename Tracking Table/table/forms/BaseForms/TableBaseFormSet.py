from django import forms

class TableFormSet(forms.BaseInlineFormSet):
    
    """ Intermediate domain level base inline formset with styled deletion widget. """
    
    deletion_widget = forms.CheckboxInput(attrs={
        "style": "width: 30px; height: 15px;",
        "class": "form-check-input",
        "role": "switch",
    })