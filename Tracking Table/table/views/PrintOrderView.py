from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from table import models

class PrintOrder(LoginRequiredMixin, TemplateView):
    model = models.Order
    template_name = 'table/printOrder.html'
    
    def get_context_data(self, pk, **kwargs):
        context = super(PrintOrder, self).get_context_data(**kwargs)
        context['order'] = models.Order.objects.get(pk=pk)
        context['order_plates'] = models.Plate.objects.filter(order_id=pk)
        context['order_edges'] = models.Edge.objects.filter(order_id=pk)
        context['order_cutting'] = models.Cutting.objects.filter(order_id=pk)
        context['order_edging'] = models.Edging.objects.filter(order_id=pk)
        context['order_others'] = models.Other.objects.filter(order_id=pk)
        context['order_payments'] = models.Payment.objects.filter(order_id=pk)

        return context