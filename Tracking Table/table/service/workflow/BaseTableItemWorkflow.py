from django.conf import settings

from common.service import BaseWorkflow
from table.service import OrderTotals, OrderWeight

_WEIGHT_ITEM_TYPES = {"Plate", "Edge"}


class BaseTableItemWorkflow(BaseWorkflow):

    @classmethod
    def pre_save(cls, item):
        item.value = cls.calculate_value(item.quantity, item.price)

    @classmethod
    def after_commit(cls, instance):
        OrderTotals.update_total(instance)
        if (
            settings.DJANGO_FEATURES__ORDER_WEIGHT
            and instance.__class__.__name__ in _WEIGHT_ITEM_TYPES
        ):
            OrderWeight.update_weight(instance.order_id)
