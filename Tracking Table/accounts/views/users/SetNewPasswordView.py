from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import PasswordResetConfirmView
from django.urls import reverse_lazy

from accounts.forms import UserSetPasswordForm
from accounts.helpers.devices.device_cookie import append_device
from accounts.helpers.devices.device_label import attach_device_client_hints
from accounts.helpers.users.set_password_token_generator import SET_PASSWORD_TOKEN_GENERATOR


class SetNewPassword(PasswordResetConfirmView):

    """

    Hierarchy:
    PasswordResetConfirmView -> SetNewPassword

    Public page for the emailed one-time set-password link.
    There is no self-serve request form on login.

    """

    form_class = UserSetPasswordForm
    template_name = "accounts/set-password.html"
    success_url = reverse_lazy("accounts:login")
    title = "Задайте парола"
    token_generator = SET_PASSWORD_TOKEN_GENERATOR

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if settings.DJANGO_FEATURES__BROWSER_COOKIE_FILTER:
            attach_device_client_hints(response)
        return response

    def form_valid(self, form):
        messages.success(
            self.request,
            "Паролата е зададена. Влезте с потребителското си име.",
        )
        enroll_browser = (
            settings.DJANGO_FEATURES__BROWSER_COOKIE_FILTER
            and not form.user.has_usable_password()
        )
        response = super().form_valid(form)
        if enroll_browser:
            append_device(self.request, response, form.user)
        return response
