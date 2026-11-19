""" Template values that come from process settings, not the request user. """

from django.conf import settings


def viewport_scale(request):
    return {
        "responsive_viewport_scale": settings.DJANGO_FEATURES__RESPONSIVE_SCALE,
    }
