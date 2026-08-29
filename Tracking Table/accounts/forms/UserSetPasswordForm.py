from django.contrib.auth.forms import SetPasswordForm


class UserSetPasswordForm(SetPasswordForm):

    """

    Hierarchy:
    SetPasswordForm -> UserSetPasswordForm

    """

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.fields["new_password1"].label = "Нова парола"
        self.fields["new_password1"].help_text = ""
        self.fields["new_password2"].label = "Повторете паролата"
        self.fields["new_password2"].help_text = ""
