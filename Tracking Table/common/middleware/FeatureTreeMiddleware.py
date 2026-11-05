from django.conf import settings
from django.shortcuts import redirect


# Old full-page boards, create, and edit. The dynamic board still calls
# view, print, history, delete, and the order-form modal under these prefixes.
_STATIC_EXACT = ("/table", "/table/", "/vitrine", "/vitrine/")
_STATIC_PREFIXES = (
    "/table/createOrder/",
    "/table/editOrder/",
    "/table/updateOrder/",
    "/vitrine/create_vitrine/",
    "/vitrine/edit_vitrine/",
    "/vitrine/update_vitrine/",
)

_DYNAMIC_EXACT = ("/dynamic", "/dynamic/")
_DYNAMIC_PREFIXES = (
    "/dynamic/data/",
    "/table/orderForm",
    "/vitrine/orderForm",
    "/table/updateProgress/",
    "/vitrine/update_progress/",
)


def _matches(path, exact, prefixes):
    if path in exact:
        return True
    return any(path.startswith(prefix) for prefix in prefixes)


class FeatureTreeMiddleware:

    """

    One feature flag, one tree.

    Dynamic on: old list/create/edit URLs go to /dynamic/.
    Dynamic off: /dynamic/ and the modal/progress URLs go to /table/.

    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated:
            return self.get_response(request)
        path = request.path
        dynamic_on = getattr(settings, "DJANGO_FEATURES__DYNAMIC_CONTENT_LOADING", False)
        if dynamic_on and _matches(path, _STATIC_EXACT, _STATIC_PREFIXES):
            return redirect("dynamic")
        if not dynamic_on and _matches(path, _DYNAMIC_EXACT, _DYNAMIC_PREFIXES):
            return redirect("table")
        return self.get_response(request)
