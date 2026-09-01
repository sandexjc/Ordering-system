from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from accounts.helpers.user_is_app_admin import deactivate_blocked_reason
from accounts.mixins import AdminRequiredMixin
from accounts.models import User


class SetUserActive(AdminRequiredMixin, View):

    """

    Hierarchy:
    AdminRequiredMixin -> SetUserActive
    View -> SetUserActive

    Admin-only activate / deactivate. POST only. No hard delete.

    """

    http_method_names = ["post"]

    def post(self, request, pk):
        target = get_object_or_404(User, pk=pk)
        activate = request.POST.get("activate") == "1"
        if not activate:
            blocked = deactivate_blocked_reason(request.user, target)
            if blocked:
                messages.error(request, blocked)
                return redirect("accounts:view-users")
        target.is_active = activate
        target.save(update_fields=["is_active"])
        if activate:
            messages.success(request, "Потребителят е активиран.")
        else:
            messages.success(request, "Потребителят е деактивиран.")
        return redirect("accounts:view-users")
