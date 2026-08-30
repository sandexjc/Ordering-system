from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView

from accounts.helpers.send_set_password_email import (
    CHANGE_PASSWORD_EMAIL_SUBJECT,
    CHANGE_PASSWORD_EMAIL_TEMPLATE,
    send_set_password_email,
)
from accounts.models import User


class ChangePassword(LoginRequiredMixin, TemplateView):

    """

    Hierarchy:
    LoginRequiredMixin -> ChangePassword
    TemplateView -> ChangePassword

    GET shows the send-email page. POST emails a one-time set-password
    link to the logged-in user. No password form; no forgot-password on login.

    """

    template_name = "accounts/change-password.html"

    def post(self, request, *args, **kwargs):
        user = User.objects.filter(pk=request.user.pk).first() or request.user
        try:
            sent = send_set_password_email(
                request,
                user,
                subject=CHANGE_PASSWORD_EMAIL_SUBJECT,
                email_template=CHANGE_PASSWORD_EMAIL_TEMPLATE,
            )
        except Exception:
            messages.error(
                request,
                "Имейлът за смяна на парола не беше изпратен.",
            )
            return redirect("accounts:change-password")

        if sent:
            messages.success(
                request,
                "Изпратен е имейл за смяна на парола.",
            )
        else:
            messages.error(
                request,
                "Профилът няма имейл адрес.",
            )
        return redirect("accounts:change-password")
