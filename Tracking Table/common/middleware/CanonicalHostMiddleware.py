from django.conf import settings
from django.core.exceptions import DisallowedHost
from django.http import HttpResponsePermanentRedirect


def canonical_hostname(hostname):
    hostname = (hostname or "").lower().strip(".")
    if hostname == "127.0.0.1":
        return "localhost"
    if hostname.startswith("www.") and hostname[4:]:
        return hostname[4:]
    return hostname


def public_site_host():
    hosts = [host for host in settings.ALLOWED_HOSTS if host and host != "*"]
    canonical_hosts = []
    for host in hosts:
        name = canonical_hostname(host.split(":")[0])
        if name not in canonical_hosts:
            canonical_hosts.append(name)
    if len(canonical_hosts) == 1:
        return canonical_hosts[0]
    if settings.DEBUG:
        return "localhost:8000"
    return None


class CanonicalHostMiddleware:

    """

    Hierarchy:
    CanonicalHostMiddleware

    Sends www.<host> to <host>, and 127.0.0.1 to localhost, before a device
    cookie is checked. One host keeps one cookie.

    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            host = request.get_host()
        except DisallowedHost:
            return self.get_response(request)
        hostname = host.split(":")[0]
        canonical = canonical_hostname(hostname)
        if canonical == hostname:
            return self.get_response(request)
        port = request.get_port()
        netloc = canonical if port in ("80", "443") else "%s:%s" % (canonical, port)
        scheme = "https" if settings.DJANGO_SECURITY_ENABLE else request.scheme
        return HttpResponsePermanentRedirect(
            "%s://%s%s" % (scheme, netloc, request.get_full_path())
        )
