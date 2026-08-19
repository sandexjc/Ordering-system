from urllib.parse import urlparse

from django.http import JsonResponse
from django.urls import reverse


class AjaxLoginRedirectMiddleware:
    """
    LoginRequiredMixin answers anonymous users with a 302 to the login page.
    Browser fetch() follows that redirect and the client sees 200 HTML, so the
    dynamic board keeps polling instead of sending the user to login.

    AJAX requests (X-Requested-With: XMLHttpRequest) get 401 JSON instead.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if not self._is_ajax_login_redirect(request, response):
            return response
        return JsonResponse({"error": "unauthenticated"}, status=401)

    def _is_ajax_login_redirect(self, request, response):
        if response.status_code not in (301, 302, 303, 307, 308):
            return False
        if request.headers.get("X-Requested-With") != "XMLHttpRequest":
            return False
        location = response.get("Location") or ""
        location_path = urlparse(location).path.rstrip("/")
        return location_path == reverse("accounts:login").rstrip("/")
