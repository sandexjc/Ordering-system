from django import forms

from accounts.models.user.UserPreferenceModel import (
    ACCENT_CHOICES,
    BACKGROUND_CHOICES,
    ROW_DENSITY_CHOICES,
    TEXT_SIZE_CHOICES,
    THEME_CHOICES,
)


class UserPreferenceForm(forms.Form):

    """

    Hierarchy:
    Form -> UserPreferenceForm

    """

    theme = forms.ChoiceField(choices=THEME_CHOICES, label="Тема")
    background = forms.ChoiceField(choices=BACKGROUND_CHOICES, label="Фон")
    accent = forms.ChoiceField(choices=ACCENT_CHOICES, label="Акцент")
    text_size = forms.ChoiceField(choices=TEXT_SIZE_CHOICES, label="Размер на текста")
    row_density = forms.ChoiceField(choices=ROW_DENSITY_CHOICES, label="Оформление")
    reduced_motion = forms.ChoiceField(
        choices=(
            ("off", "Включено"),
            ("reduce", "Изключено"),
        ),
        label="Анимации",
    )
