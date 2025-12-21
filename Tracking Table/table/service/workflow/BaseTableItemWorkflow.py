from common.service import BaseWorkflow
from table.service import OrderTotals

class BaseTableItemWorkflow(BaseWorkflow):

    @classmethod
    def pre_save(cls, item):
        item.value = cls.calculate_value(item.quantity, item.price)

    @classmethod
    def after_commit(cls, instance):
        OrderTotals.update_total(instance)
