from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView
from django.shortcuts import redirect
from django.http import JsonResponse
from django.core import serializers

from table.models import Order
from table.forms import PlateProgressFormSet, EdgeProgressFormSet, OrderProgressForm

import json

class UpdateOrder(LoginRequiredMixin, UpdateView):

    model = Order

    def post(self, request, pk, *args, **kwargs):

        self.object = Order.objects.get_by_id(pk)
        plates_progress = PlateProgressFormSet(self.request.POST, instance=self.object)
        edges_progress = EdgeProgressFormSet(self.request.POST, instance=self.object)
        order_progress = OrderProgressForm(self.request.POST, instance=self.object)

        if plates_progress.is_valid() and edges_progress.is_valid() and order_progress.is_valid():
            return self.form_valid(plates_progress, edges_progress, order_progress, self.object)
        else:
            print(plates_progress.errors)
            print(edges_progress.errors)
            return redirect('/')

    def form_valid(self, plates_progress, edges_progress, order_progress, order):

        plates_data = plates_progress.save(commit=False)
        edges_data = edges_progress.save(commit=False)

        for item in plates_data:
            item.save()

        for item in edges_data:
            item.save()

        if self.check_if_ready(order, plates_data, edges_data):
            order.order_ready = True
            order.save()
            order_progress.save()
        else:
            order.order_ready = False
            order.order_taken = False
            order.save()
        
        return JsonResponse({
            'order':    json.loads(serializers.serialize('json', [order])),
            'plates':   json.loads(serializers.serialize('json', order.plates.all())),
            'edges':    json.loads(serializers.serialize('json', order.edges.all())),
            })

    def check_if_ready(self, order, plates, edges):

        for item in plates:
            if not item.ordered or not item.delivered or not item.cutted or not item.edged:
                return False

        return True