from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from table.models import Order

class PrintOrder(LoginRequiredMixin, TemplateView):
    model = Order
    template_name = 'table/print_order.html'
    
    def get_context_data(self, pk, **kwargs):
        context = super(PrintOrder, self).get_context_data(**kwargs)
        context['order'] = Order.objects.get_by_id(pk)

        return context