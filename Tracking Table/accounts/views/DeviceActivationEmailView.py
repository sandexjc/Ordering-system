from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, JsonResponse
from django.views import View

from accounts.helpers.devices.send_device_activation_email import send_device_activation_email


class DeviceActivationEmail(LoginRequiredMixin, View):

    """

    Hierarchy:
    LoginRequiredMixin -> DeviceActivationEmail
    View -> DeviceActivationEmail

    Emails a one-time device link to the logged-in user. POST only.

    """

    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        if not settings.DJANGO_FEATURES__BROWSER_COOKIE_FILTER:
            raise Http404()
        try:
            sent = send_device_activation_email(
                request,
                request.user,
                device_name=request.POST.get("device_name", ""),
            )
        except Exception:
            return JsonResponse({"ok": False})
        return JsonResponse({"ok": bool(sent)})
