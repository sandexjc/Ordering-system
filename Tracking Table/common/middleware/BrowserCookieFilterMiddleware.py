from django.conf import settings
from django.http import HttpResponseForbidden
from django.urls import Resolver404, resolve

from accounts.helpers.devices.device_cookie import (
    EXEMPT_URL_NAMES,
    cookie_has_active_device,
    touch_active_devices,
)


class BrowserCookieFilterMiddleware:

    """

    When DJANGO_FEATURES__BROWSER_COOKIE_FILTER is on, a browser with no
    active device secret receives 403 for every Django response. The
    set-password page and the reserved activate-device page stay open.
    The flag off leaves the request unchanged.

    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not settings.DJANGO_FEATURES__BROWSER_COOKIE_FILTER:
            return self.get_response(request)
        if self._is_exempt(request):
            return self.get_response(request)
        if not cookie_has_active_device(request):
            return HttpResponseForbidden()
        touch_active_devices(request)
        return self.get_response(request)

    def _is_exempt(self, request):
        try:
            match = resolve(request.path_info)
        except Resolver404:
            return False
        return (
            match.namespace == "accounts"
            and match.url_name in EXEMPT_URL_NAMES
        )
