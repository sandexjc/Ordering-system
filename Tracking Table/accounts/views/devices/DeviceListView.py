from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse
from django.views import View

from accounts.helpers.devices.device_list import device_list_item, enrolled_devices
from accounts.helpers.devices.device_subject import device_subject
from common.mixins import DynamicFeatureFlagRequiredMixin


class DeviceList(LoginRequiredMixin, DynamicFeatureFlagRequiredMixin, View):

    """

    Hierarchy:
    LoginRequiredMixin -> DeviceList
    DynamicFeatureFlagRequiredMixin -> DeviceList
    View -> DeviceList

    JSON list of active devices. Without pk, the logged-in user.
    With pk, that user, for an admin.

    """

    feature_setting_name = "DJANGO_FEATURES__BROWSER_COOKIE_FILTER"
    feature_disabled_message = "Browser cookie filter is disabled."
    http_method_names = ["get"]

    def get(self, request, pk=None, *args, **kwargs):
        subject = device_subject(request, pk)
        devices = enrolled_devices(subject.pk)
        return JsonResponse({
            "devices": [
                device_list_item(device, self._revoke_url(subject, device, pk))
                for device in devices
            ],
        })

    def _revoke_url(self, subject, device, user_pk):
        if user_pk is None:
            return reverse("accounts:revoke-profile-device", kwargs={"pk": device.pk})
        return reverse(
            "accounts:revoke-user-device",
            kwargs={"pk": subject.pk, "device_pk": device.pk},
        )
