from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from table.models import Order
from table.forms import PlateProgressFormSet, EdgeProgressFormSet, OrderProgressForm

class ViewOrder(LoginRequiredMixin, TemplateView):
    template_name = 'order.html'

    def get_context_data(self, pk, **kwargs):
        context = super(ViewOrder, self).get_context_data(**kwargs)
        context['order'] = Order.objects.get_by_id(pk)
        
        # Only placed orders ( not offers ) can be tracked
        if context['order'].client == "Internal":
            # FIXME create formsets on request
            context['plate_forms'] = PlateProgressFormSet(instance=context['order'])
            context['edge_forms'] = EdgeProgressFormSet(instance=context['order'])
            context['order_progress'] = OrderProgressForm(instance=context['order'])

        return context
    
    def post(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())