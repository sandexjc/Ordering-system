from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View

from accounts.helpers.devices.device_cookie import revoke_device
from accounts.helpers.devices.device_subject import device_subject
from accounts.models import Device
from common.mixins import DynamicFeatureFlagRequiredMixin


class RevokeDevice(LoginRequiredMixin, DynamicFeatureFlagRequiredMixin, View):

    """

    Hierarchy:
    LoginRequiredMixin -> RevokeDevice
    DynamicFeatureFlagRequiredMixin -> RevokeDevice
    View -> RevokeDevice

    Revokes one active device. Without device_pk, pk is the device and the
    owner is the logged-in user. With device_pk, pk is the user, for an admin.
    POST only.

    """

    feature_setting_name = "DJANGO_FEATURES__BROWSER_COOKIE_FILTER"
    feature_disabled_message = "Browser cookie filter is disabled."
    http_method_names = ["post"]

    def post(self, request, pk, device_pk=None, *args, **kwargs):
        if device_pk is None:
            subject = device_subject(request)
            device_id = pk
        else:
            subject = device_subject(request, pk)
            device_id = device_pk
        device = get_object_or_404(
            Device,
            pk=device_id,
            user_id=subject.pk,
            revoked_at__isnull=True,
            secret_hash__isnull=False,
        )
        response = JsonResponse({"ok": True})
        revoke_device(request, response, device)
        return response
