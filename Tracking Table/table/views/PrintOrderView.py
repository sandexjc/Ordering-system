from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from table.models import (
    Order, Plate, Edge, Cutting,
    Edging, Other, Payment
)

class PrintOrder(LoginRequiredMixin, TemplateView):
    model = Order
    template_name = 'table/print_order.html'
    
    def get_context_data(self, pk, **kwargs):
        context = super(PrintOrder, self).get_context_data(**kwargs)

        context['order'] = Order.objects.get_by_id(pk)
        context['order_plates'] = Plate.objects.for_order_id(pk)
        context['order_edges'] = Edge.objects.for_order_id(pk)
        context['order_cutting'] = Cutting.objects.for_order_id(pk)
        context['order_edging'] = Edging.objects.for_order_id(pk)
        context['order_others'] = Other.objects.for_order_id(pk)
        context['order_payments'] = Payment.objects.for_order_id(pk)

        return context