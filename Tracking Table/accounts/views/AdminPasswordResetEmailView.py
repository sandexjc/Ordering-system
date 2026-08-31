from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from accounts.helpers.send_set_password_email import send_set_password_email
from accounts.mixins import AdminRequiredMixin
from accounts.models import User


class AdminPasswordResetEmail(AdminRequiredMixin, View):

    """

    Hierarchy:
    AdminRequiredMixin -> AdminPasswordResetEmail
    View -> AdminPasswordResetEmail

    Admin-only send of the set-password email to another user. POST only.

    """

    http_method_names = ["post"]

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        try:
            sent = send_set_password_email(request, user)
        except Exception:
            return self._respond(request, False)

        return self._respond(request, sent)

    def _respond(self, request, sent):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": bool(sent)})
        if sent:
            messages.success(
                request,
                "Изпратен е имейл за задаване на парола.",
            )
        else:
            messages.error(
                request,
                "Имейлът за задаване на парола не беше изпратен.",
            )
        return redirect("accounts:view-users")
