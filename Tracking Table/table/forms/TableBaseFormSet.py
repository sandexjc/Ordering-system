from django import forms

class CustomTableInlineFormSet(forms.BaseInlineFormSet):
    
    # Reusable inline formset with styled deletion widget.
    
    deletion_widget = forms.CheckboxInput(attrs={
        "style": "width: 30px; height: 15px;",
        "class": "form-check-input",
        "role": "switch",
    })