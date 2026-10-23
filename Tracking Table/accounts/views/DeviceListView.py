from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.views import View

from accounts.models import Device


class DeviceList(LoginRequiredMixin, View):

    """

    Hierarchy:
    LoginRequiredMixin -> DeviceList
    View -> DeviceList

    JSON list of the logged-in user's active devices.

    """

    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        if not settings.DJANGO_FEATURES__BROWSER_COOKIE_FILTER:
            raise Http404()
        devices = Device.objects.filter(
            user_id=request.user.pk,
            revoked_at__isnull=True,
            secret_hash__isnull=False,
        ).order_by("-created_at")
        return JsonResponse({
            "devices": [
                {
                    "id": device.pk,
                    "device_name": device.device_name or ("Устройство %s" % device.pk),
                    "created_at": _format_timestamp(device.created_at),
                    "last_used_at": _format_timestamp(device.last_used_at),
                    "revoke_url": reverse("accounts:revoke-profile-device", kwargs={"pk": device.pk}),
                }
                for device in devices
            ],
        })


def _format_timestamp(value):
    if value is None:
        return ""
    return timezone.localtime(value).strftime("%d/%m/%Y %H:%M")
