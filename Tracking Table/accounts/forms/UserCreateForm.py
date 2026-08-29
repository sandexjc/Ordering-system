from django import forms

from accounts.models import User


class UserCreateForm(forms.ModelForm):

    """

    Hierarchy:
    ModelForm -> UserCreateForm

    """

    class Meta:

        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
        )

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Потребителско име"
        self.fields["username"].required = True
        self.fields["username"].help_text = ""
        self.fields["first_name"].label = "Име"
        self.fields["first_name"].required = True
        self.fields["last_name"].label = "Фамилия"
        self.fields["email"].label = "Имейл"
        self.fields["email"].required = True
        self.fields["role"].label = "Група"
        self.fields["role"].required = True

    def save(self, commit=True):

        user = super().save(commit=False)
        user.set_unusable_password()
        if commit:
            user.save()
        return user
