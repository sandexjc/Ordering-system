from django import forms

from accounts.models.user.UserPreferenceModel import BACKGROUND_CHOICES, THEME_CHOICES


class UserPreferenceForm(forms.Form):

    """

    Hierarchy:
    Form -> UserPreferenceForm

    """

    theme = forms.ChoiceField(choices=THEME_CHOICES, label="Тема")
    background = forms.ChoiceField(choices=BACKGROUND_CHOICES, label="Фон")
