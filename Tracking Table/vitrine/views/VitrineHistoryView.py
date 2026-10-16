from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.http import JsonResponse
from django.views.generic import ListView

import json

from vitrine.models import Change, Vitrine


class VitrineHistory(LoginRequiredMixin, ListView):

    """

    Hierarchy:
    LoginRequiredMixin -> VitrineHistory
    ListView -> VitrineHistory

    """

    model = Vitrine

    def get(self, request, pk, *args, **kwargs):
        changes = Change.objects.for_order_id(pk)
        if not changes:
            return JsonResponse({
                "changes": "NO DATA",
            })
        return JsonResponse({
            "changes": json.loads(serializers.serialize("json", Change.objects.filter(vitrine_id=pk))),
        })
