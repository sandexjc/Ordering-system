from django.contrib.auth.forms import AuthenticationForm

from accounts.models import User


class LoginForm(AuthenticationForm):

    """

    Hierarchy:
    AuthenticationForm -> LoginForm

    """

    class Meta:

        fields = ("username", "password")
        model = User

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Username"
        self.fields["password"].label = "Password"
        self.fields["username"].widget.attrs["placeholder"] = "Type your username"
        self.fields["password"].widget.attrs["placeholder"] = "Type your password"
