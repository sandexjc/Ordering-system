from django import forms

class FormSetStyleMixin:

    """

    Hierarchy:
    FormSetStyleMixin

    --- Fields inherited from parent classes ---

    No inherited class fields.

    """

    deletion_widget = forms.CheckboxInput(attrs={
        "style": "width: 30px; height: 15px;",
        "class": "form-check-input",
        "role": "switch",
    })