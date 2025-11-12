from django import forms

class FormSetStyleMixin:

    """ Mixin that provides consistent styling for formset-level widgets. """

    deletion_widget = forms.CheckboxInput(attrs={
        "style": "width: 30px; height: 15px;",
        "class": "form-check-input",
        "role": "switch",
    })