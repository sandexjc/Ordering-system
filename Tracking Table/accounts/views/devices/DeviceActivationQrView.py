from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse
from django.views import View

from accounts.helpers.devices.device_activation import activation_for_user
from common.mixins import DynamicFeatureFlagRequiredMixin
from common.qr import qr_svg


class DeviceActivationQr(LoginRequiredMixin, DynamicFeatureFlagRequiredMixin, View):

    """

    Hierarchy:
    LoginRequiredMixin -> DeviceActivationQr
    DynamicFeatureFlagRequiredMixin -> DeviceActivationQr
    View -> DeviceActivationQr

    Picture of the logged-in user's device activation link. POST only.
    Admins email a link from the user list. They do not get this picture.

    """

    feature_setting_name = "DJANGO_FEATURES__BROWSER_COOKIE_FILTER"
    feature_disabled_message = "Browser cookie filter is disabled."
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        target = request.user
        link = activation_for_user(request, target)
        if link is None:
            raise Http404(self.feature_disabled_message)
        _device, url = link
        response = HttpResponse(qr_svg(url), content_type="image/svg+xml")
        response["Cache-Control"] = "no-store"
        response["X-Can-Email"] = "1" if getattr(target, "email", "") else "0"
        return response
