from django.contrib.auth.forms import AuthenticationForm

from accounts.models import User


class LoginForm(AuthenticationForm):

    """

    Hierarchy:
    AuthenticationForm -> LoginForm

    """

    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": "Грешно потребителско име или парола.",
        "inactive": "Този акаунт е неактивен.",
    }

    class Meta:

        fields = ("username", "password")
        model = User

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Потребителско име"
        self.fields["password"].label = "Парола"
        self.fields["username"].error_messages["required"] = "Това поле е задължително."
        self.fields["password"].error_messages["required"] = "Това поле е задължително."
