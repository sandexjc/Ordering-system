from common.service import BaseWorkflow
from table.service import OrderTotals

class PaymentWorkflow(BaseWorkflow):

    @classmethod
    def pre_save(cls, item):
        pass

    @classmethod
    def after_commit(cls, instance):
        OrderTotals.update_total(instance)
