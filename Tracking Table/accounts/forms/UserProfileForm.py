from django import forms
from django.contrib.auth import get_user_model


class UserProfileForm(forms.ModelForm):

    """

    Hierarchy:
    ModelForm -> UserProfileForm

    """

    class Meta:

        model = get_user_model()
        fields = (
            "first_name",
            "last_name",
            "email",
        )

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.fields["first_name"].label = "Име"
        self.fields["first_name"].required = True
        self.fields["last_name"].label = "Фамилия"
        self.fields["email"].label = "Имейл"
        self.fields["email"].required = True
        self.fields["email"].help_text = ""
