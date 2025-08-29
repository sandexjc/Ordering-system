from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from common import custom_classes
from table.models import Order

class ViewOrder(LoginRequiredMixin, TemplateView):
    template_name = 'order.html'

    def get_context_data(self, pk, **kwargs):
        context = super(ViewOrder, self).get_context_data(**kwargs)
        context['order'] = custom_classes.OrderObject(Order.objects.filter(id=pk).first())
        return context
    
    def post(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())