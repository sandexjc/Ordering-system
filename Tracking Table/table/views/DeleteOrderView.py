from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DeleteView
from table.models import Order
from django.http import JsonResponse

class DeleteOrder(LoginRequiredMixin, DeleteView):

    model = Order
    
    def post(self, request, pk, *args, **kwargs):

        self.object = Order.objects.get_by_id(pk)
        self.object.delete()

        return JsonResponse({
            'status':'OK',
            })