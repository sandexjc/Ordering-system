from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from accounts.helpers.user_is_app_admin import role_change_blocked_reason
from accounts.mixins import AdminRequiredMixin
from accounts.models import User


class SetUserRole(AdminRequiredMixin, View):

    """

    Hierarchy:
    AdminRequiredMixin -> SetUserRole
    View -> SetUserRole

    Admin-only role change. POST only.

    """

    http_method_names = ["post"]

    def post(self, request, pk):
        target = get_object_or_404(User, pk=pk)
        new_role = request.POST.get("role", "")
        blocked = role_change_blocked_reason(request.user, target, new_role)
        if blocked:
            return self._respond(
                request,
                ok=False,
                role=target.role,
                error=blocked,
            )
        if target.role != new_role:
            target.role = new_role
            target.save(update_fields=["role"])
        return self._respond(request, ok=True, role=target.role)

    def _respond(self, request, ok, role, error=None):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            payload = {"ok": ok, "role": role}
            if error:
                payload["error"] = error
            return JsonResponse(payload)
        if ok:
            messages.success(request, "Групата на потребителя е променена.")
        elif error:
            messages.error(request, error)
        return redirect("accounts:view-users")
