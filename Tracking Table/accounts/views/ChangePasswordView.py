from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
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
            return self._respond(request, False)

        return self._respond(request, sent)

    def _respond(self, request, sent):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": bool(sent)})
        return redirect("accounts:change-password")
