from django.contrib import messages
from django.contrib.auth.views import PasswordResetConfirmView
from django.urls import reverse_lazy

from accounts.forms import UserSetPasswordForm
from accounts.helpers.set_password_token_generator import SET_PASSWORD_TOKEN_GENERATOR


class SetPassword(PasswordResetConfirmView):

    """

    Hierarchy:
    PasswordResetConfirmView -> SetPassword

    Public page for the emailed one-time set-password link.
    There is no self-serve request form; only an Admin can send the email.

    """

    form_class = UserSetPasswordForm
    template_name = "accounts/set-password.html"
    success_url = reverse_lazy("accounts:login")
    title = "Задайте парола"
    token_generator = SET_PASSWORD_TOKEN_GENERATOR

    def form_valid(self, form):
        messages.success(
            self.request,
            "Паролата е зададена. Влезте с потребителското си име.",
        )
        return super().form_valid(form)
