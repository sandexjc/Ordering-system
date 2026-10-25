from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View

from accounts.helpers.devices.device_subject import device_subject
from accounts.helpers.devices.send_device_activation_email import send_device_activation_email
from common.mixins import DynamicFeatureFlagRequiredMixin


class DeviceActivationEmail(LoginRequiredMixin, DynamicFeatureFlagRequiredMixin, View):

    """

    Hierarchy:
    LoginRequiredMixin -> DeviceActivationEmail
    DynamicFeatureFlagRequiredMixin -> DeviceActivationEmail
    View -> DeviceActivationEmail

    Emails a one-time device link. Without pk, to the logged-in user.
    With pk, to that user, for an admin. POST only.

    """

    feature_setting_name = "DJANGO_FEATURES__BROWSER_COOKIE_FILTER"
    feature_disabled_message = "Browser cookie filter is disabled."
    http_method_names = ["post"]

    def post(self, request, pk=None, *args, **kwargs):
        target = device_subject(request, pk)
        try:
            sent = send_device_activation_email(request, target)
        except Exception:
            return JsonResponse({"ok": False})
        return JsonResponse({"ok": bool(sent)})
