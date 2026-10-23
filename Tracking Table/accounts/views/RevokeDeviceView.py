from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View

from accounts.helpers.devices.device_cookie import revoke_device
from accounts.models import Device


class RevokeDevice(LoginRequiredMixin, View):

    """

    Hierarchy:
    LoginRequiredMixin -> RevokeDevice
    View -> RevokeDevice

    Revokes one active device owned by the logged-in user. POST only.

    """

    http_method_names = ["post"]

    def post(self, request, pk, *args, **kwargs):
        if not settings.DJANGO_FEATURES__BROWSER_COOKIE_FILTER:
            raise Http404()
        device = get_object_or_404(
            Device,
            pk=pk,
            user_id=request.user.pk,
            revoked_at__isnull=True,
        )
        response = JsonResponse({"ok": True})
        revoke_device(request, response, device)
        return response
