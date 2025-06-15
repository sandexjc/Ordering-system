
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.http import JsonResponse
from django.core import serializers
import json

from table.models import Order, Change

class OrderHistory(LoginRequiredMixin, ListView):

    model = Order

    def get(self, request, pk, *args, **kwargs):

        print("GET ORDER HISTORY", pk)

        order_chnages = Change.objects.filter(cutID=pk)

        if not order_chnages:
            return JsonResponse({
            'changes': 'NO DATA',
            }) 
            
        return JsonResponse({
            'changes': json.loads(serializers.serialize('json', Change.objects.filter(cutID=pk))),
            })