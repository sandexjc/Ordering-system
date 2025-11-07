
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.http import JsonResponse
from django.core import serializers
import json

from table.models import Order, Change

class OrderHistory(LoginRequiredMixin, ListView):

    model = Order

    def get(self, request, pk, *args, **kwargs):

        order_chnages = Change.objects.for_order_id(pk)

        if not order_chnages:
            return JsonResponse({
            'changes': 'NO DATA',
            }) 
            
        return JsonResponse({
            'changes': json.loads(serializers.serialize('json', Change.objects.filter(order_id=pk))),
            })