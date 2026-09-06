from pathlib import Path

from django.contrib.staticfiles import finders
from django.http import Http404, HttpResponse
from django.views import View


class ServiceWorker(View):

    """
    Serves the site-root service worker script from static files.

    Must be at /sw.js so the worker's scope covers accounts, table, and
    vitrine URLs. HTTP caching is skipped for this script only so a new
    service-worker.js is detected; the offline page lives in Cache Storage
    and is stored once on install.

    Hierarchy:
    View -> ServiceWorker

    """

    script_name = "js/offline/service-worker.js"

    def get(self, request, *args, **kwargs):
        script_path = finders.find(self.script_name)
        if not script_path:
            raise Http404("Service worker script not found.")
        response = HttpResponse(
            Path(script_path).read_bytes(),
            content_type="application/javascript",
        )
        response["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response["Service-Worker-Allowed"] = "/"
        return response
