from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from table.models import Order, Plate
from table.forms import PlateProgressFormSet, EdgeProgressFormSet, OrderProgressForm

class ViewOrder(LoginRequiredMixin, TemplateView):
    template_name = 'order.html'

    def get_context_data(self, pk, **kwargs):
        context = super(ViewOrder, self).get_context_data(**kwargs)

        order = Order.objects.get_by_id(pk)
        plates = Plate.objects.for_order(order).select_related("order_id")
        
        context['order'] = order
        context['plate_forms'] = PlateProgressFormSet(instance=order, queryset=plates)
        context['edge_forms'] = EdgeProgressFormSet(instance=order)
        context['order_progress'] = OrderProgressForm(instance=order)

        return context
    
    def post(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())