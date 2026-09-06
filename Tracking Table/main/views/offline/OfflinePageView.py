from django.views.generic import TemplateView


class OfflinePage(TemplateView):

    """
    Public fallback page cached by the service worker.

    Shown when a later full-page navigation cannot reach the server.
    Stays login-free so the worker can fetch and cache it after install.

    Hierarchy:
    TemplateView -> OfflinePage

    """

    template_name = "components/offline.html"
