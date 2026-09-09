from pathlib import Path

from django.contrib.staticfiles import finders
from django.http import Http404, HttpResponse, HttpResponseNotModified
from django.utils.http import http_date, parse_http_date_safe
from django.views import View


class ServiceWorker(View):
    """
    Serves the site-root service worker script from static files.

    Must be at /sw.js so the worker's scope covers accounts, table, and
    vitrine URLs. The script is HTTP-cached and validated with ETag /
    Last-Modified so browser update checks can return 304 when unchanged.
    The offline page itself lives in Cache Storage and is populated by
    the worker install step.

    Hierarchy:
    View -> ServiceWorker

    """

    script_name = "js/offline/service-worker.js"

    def get(self, request, *args, **kwargs):
        script_path = finders.find(self.script_name)
        if not script_path:
            raise Http404("Service worker script not found.")
        script_stat = Path(script_path).stat()
        script_etag = 'W/"{mtime}-{size}"'.format(
            mtime=script_stat.st_mtime_ns,
            size=script_stat.st_size,
        )
        script_last_modified = int(script_stat.st_mtime)
        if_none_match = request.META.get("HTTP_IF_NONE_MATCH", "")
        if_modified_since = parse_http_date_safe(
            request.META.get("HTTP_IF_MODIFIED_SINCE", "")
        )
        if if_none_match == script_etag or (
            if_modified_since is not None and if_modified_since >= script_last_modified
        ):
            response = HttpResponseNotModified()
            response["ETag"] = script_etag
            response["Last-Modified"] = http_date(script_last_modified)
            response["Cache-Control"] = "public, max-age=86400"
            response["Service-Worker-Allowed"] = "/"
            return response
        response = HttpResponse(
            Path(script_path).read_bytes(),
            content_type="application/javascript",
        )
        response["ETag"] = script_etag
        response["Last-Modified"] = http_date(script_last_modified)
        response["Cache-Control"] = "public, max-age=86400"
        response["Service-Worker-Allowed"] = "/"
        return response
