from django.db import transaction
from decimal import Decimal, ROUND_HALF_UP

class BaseWorkflow:

    """ Base class for model workflows. Defines lifecycle hooks and execution order. """

    @staticmethod
    def calculate_value(quantity, price):
        # Return item value with proper type and rounding.
        return (quantity * price).quantize(Decimal("0.01"),rounding=ROUND_HALF_UP)

    @classmethod
    def pre_save(cls, instance):
        # Executed BEFORE model save.
        pass

    @classmethod
    def post_save(cls, instance):
        # Executed AFTER model save.
        pass

    @classmethod
    def on_delete(cls, instance):
        # Executed BEFORE soft/hard delete.
        pass

    @classmethod
    def after_commit(cls, instance):
        # Executed after post_save/delete inside same transaction.
        # Used for recalculation of order totals after items updates.
        pass

    @classmethod
    def run_save_seq(cls, instance):
        # Full save workflow (pre + save + post + after).
        with transaction.atomic():
            cls.pre_save(instance)
            instance.save()
            cls.post_save(instance)
        
        cls.after_commit(instance)

    @classmethod
    def run_delete_seq(cls, instance):
        # Full delete workflow.
        with transaction.atomic():
            cls.on_delete(instance)
            instance.soft_delete()
        
        cls.after_commit(instance)
