from common.views import BaseUpdateProgressStepView
from vitrine.models import Vitrine


class UpdateProgressStep(BaseUpdateProgressStepView):

    """

    Hierarchy:
    DynamicFeatureFlagRequiredMixin -> BaseUpdateProgressStepView -> UpdateProgressStep
    LoginRequiredMixin -> BaseUpdateProgressStepView -> UpdateProgressStep
    View -> BaseUpdateProgressStepView -> UpdateProgressStep

    Dynamic vitrine click-to-toggle for order_ready / order_taken.

    --- Fields inherited from BaseUpdateProgressStepView ---

    model = None
    allowed_fields = {}
    http_method_names = ["post"]

    """

    model = Vitrine
    allowed_fields = {
        "order": ("order_ready", "order_taken"),
    }

    def is_step_disabled(self, order, target, item, field, value):
        """order_taken cannot be set while the vitrine is not ready."""
        return field == "order_taken" and value and not order.order_ready

    def after_step_applied(self, order, target, item, field, value):
        """Same as BaseUpdateView: clear order_taken when order_ready is false."""
        if not order.order_ready and order.order_taken:
            order.order_taken = False
            order.save()
