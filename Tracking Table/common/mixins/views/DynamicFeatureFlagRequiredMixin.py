from django.conf import settings
from django.http import Http404


class DynamicFeatureFlagRequiredMixin:

    """

    Hierarchy:
    DynamicFeatureFlagRequiredMixin

    --- Fields inherited from parent classes ---

    No inherited class fields.

    """

    feature_setting_name = "DJANGO_FEATURES__DYNAMIC_CONTENT_LOADING"
    feature_disabled_message = "Dynamic content loading feature is disabled."

    def is_dynamic_feature_enabled(self):
        return getattr(settings, self.feature_setting_name, False)

    def dispatch(self, request, *args, **kwargs):
        if not self.is_dynamic_feature_enabled():
            raise Http404(self.feature_disabled_message)
        return super().dispatch(request, *args, **kwargs)
