from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView
from django.shortcuts import redirect
from django.http import JsonResponse

from table.models import Order
from table.forms import PlateProgressFormSet, EdgeProgressFormSet, OrderProgressForm
from common import custom_classes

class UpdateOrder(LoginRequiredMixin, UpdateView):

    model = Order

    def post(self, request, pk, *args, **kwargs):

        print('UPDATE ORDER ->', pk)

        self.object = Order.objects.get(pk=pk)
        PLATES_PROG = PlateProgressFormSet(self.request.POST, instance=self.object)
        EDGES_PROG = EdgeProgressFormSet(self.request.POST, instance=self.object)
        ORDER_PROG = OrderProgressForm(self.request.POST, instance=self.object)

        print('<<--------------------------------->>')

        if PLATES_PROG.is_valid() and EDGES_PROG.is_valid() and ORDER_PROG.is_valid():
            print('FORM VALID')
            return self.form_valid(PLATES_PROG, EDGES_PROG, ORDER_PROG, self.object)
        else:
            print('FORM INVALID _____________')
            print('PLATES ERRORS:')
            print(PLATES_PROG.errors)
            print('EDGES ERRORS:')
            print(EDGES_PROG.errors)
            return redirect('/')

    def form_valid(self, PLATES_PROG, EDGES_PROG, ORDER_PROG, order):

        plates_data = PLATES_PROG.save(commit=False)
        edges_data = EDGES_PROG.save(commit=False)

        for item in plates_data:
            item.save()

        for item in edges_data:
            item.save()

        if self.check_if_ready(order, plates_data, edges_data):
            order.order_ready = True
            order.save()
            ORDER_PROG.save()
        else:
            order.order_ready = False
            order.order_taken = False
            order.save()

        customObj = custom_classes.OrderDetails(order)
        
        return JsonResponse({
            'order': customObj.get_order(),
            'plates':customObj.get_plates(),
            'edges':customObj.get_edges(),
            })

    def check_if_ready(self, order, plates, edges):

        for item in plates:
            if not item.ordered or not item.delivered or not item.cutted or not item.edged:
                return False

        return True