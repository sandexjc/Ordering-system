from django.contrib import messages
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
            messages.error(
                request,
                "Имейлът за задаване на парола не беше изпратен.",
            )
            return redirect("accounts:view-users")

        if sent:
            messages.success(
                request,
                "Изпратен е имейл за задаване на парола.",
            )
        else:
            messages.error(
                request,
                "Потребителят няма имейл адрес.",
            )
        return redirect("accounts:view-users")
