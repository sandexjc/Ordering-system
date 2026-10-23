from django.conf import settings
from django.core.cache import cache


LOGIN_RATE_LIMIT_MESSAGE = "Твърде много опити за вход. Опитайте отново по-късно."


def login_client_ip(request):
    if getattr(settings, "DJANGO_SECURITY_ENABLE", False):
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[0].strip() or "unknown"
    return request.META.get("REMOTE_ADDR") or "unknown"


def _attempts_key(request):
    return "login-fail:%s" % login_client_ip(request)


def _limit():
    return int(getattr(settings, "LOGIN_RATE_LIMIT_ATTEMPTS", 5))


def _window():
    return int(getattr(settings, "LOGIN_RATE_LIMIT_WINDOW", 900))


def login_is_locked(request):
    try:
        count = int(cache.get(_attempts_key(request), 0))
    except (TypeError, ValueError):
        count = 0
    return count >= _limit()


def record_login_failure(request):
    key = _attempts_key(request)
    timeout = _window()
    try:
        cache.incr(key)
    except ValueError:
        cache.add(key, 1, timeout)


def clear_login_failures(request):
    cache.delete(_attempts_key(request))
