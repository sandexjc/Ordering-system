from django.conf import settings
from django.shortcuts import redirect


class StaticTreeClosedMixin:

    """

    Hierarchy:
    StaticTreeClosedMixin

    When dynamic loading is on, this view redirects to /dynamic/.

    """

    def dispatch(self, request, *args, **kwargs):
        if getattr(settings, "DJANGO_FEATURES__DYNAMIC_CONTENT_LOADING", False):
            return redirect("dynamic")
        return super().dispatch(request, *args, **kwargs)
