from django.contrib import messages
from django.http import JsonResponse
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
                return self._respond(
                    request,
                    ok=False,
                    is_active=target.is_active,
                    error=blocked,
                )
        target.is_active = activate
        target.save(update_fields=["is_active"])
        return self._respond(request, ok=True, is_active=activate)

    def _respond(self, request, ok, is_active, error=None):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            payload = {"ok": ok, "is_active": is_active}
            if error:
                payload["error"] = error
            return JsonResponse(payload)
        if ok:
            if is_active:
                messages.success(request, "Потребителят е активиран.")
            else:
                messages.success(request, "Потребителят е деактивиран.")
        elif error:
            messages.error(request, error)
        return redirect("accounts:view-users")
