from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect
from django.views.generic import TemplateView

from accounts.helpers.devices.device_cookie import enroll_device
from accounts.helpers.devices.send_device_activation_email import activation_from_link


class ActivateDevice(TemplateView):

    """

    Hierarchy:
    TemplateView -> ActivateDevice

    Public confirm page for the device-activation email.
    GET shows the button. POST adds the device cookie.

    """

    template_name = "accounts/activate-device.html"

    def dispatch(self, request, *args, **kwargs):
        if not settings.DJANGO_FEATURES__BROWSER_COOKIE_FILTER:
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        device = activation_from_link(kwargs["uidb64"], kwargs["token"])
        return self.render_to_response(self._context(device))

    def post(self, request, *args, **kwargs):
        device = activation_from_link(kwargs["uidb64"], kwargs["token"])
        if device is None:
            return self.render_to_response(self._context(None))
        response = redirect("accounts:login")
        enroll_device(request, response, device)
        messages.success(
            request,
            "Устройството е добавено. Влезте с потребителското си име.",
        )
        return response

    def _context(self, device):
        if device is None:
            return {"validlink": False, "username": "", "device_name": ""}
        return {
            "validlink": True,
            "username": device.user.username,
            "device_name": device.device_name,
        }
