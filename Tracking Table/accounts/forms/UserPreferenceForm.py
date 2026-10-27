from django import forms

from accounts.models.user.UserPreferenceModel import THEME_CHOICES


class UserPreferenceForm(forms.Form):

    """

    Hierarchy:
    Form -> UserPreferenceForm

    """

    theme = forms.ChoiceField(choices=THEME_CHOICES, label="Тема")
