from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from common.service import CurrencyOperations


class BasePrintView(LoginRequiredMixin, TemplateView):

    """ Base class for print views across multiple apps with shared logic. """

    # Subclasses must define the below properties
    model = None
    template_name = None
    order_context = None
    
    def get_context_data(self, pk, **kwargs):
        context = super().get_context_data(pk=pk, **kwargs)

        obj = self.model.objects.get_by_id(pk)
        context[self.order_context] = obj
        context["currency"] = CurrencyOperations.get_currency(obj.created_at.date())

        return context