from django import forms
from common.mixins import FormSetStyleMixin

class TableFormSet(FormSetStyleMixin, forms.BaseInlineFormSet):

    """

    Hierarchy:
    FormSetStyleMixin -> TableFormSet
    forms.BaseInlineFormSet -> TableFormSet

    --- Fields inherited from FormSetStyleMixin ---

    deletion_widget = forms.CheckboxInput(attrs={"style": "width: 30px; height: 15px;", "class": "form-check-input", "role": "switch"})

    """

    pass