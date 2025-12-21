from django.db.models import Sum
from decimal import Decimal


class BaseTotal:

    """ Shared orders and related items totals calculations. """

    @staticmethod
    def update_item_total(order_instance, related_manager, field):
        # Calculate order related items total price.
        # Save the result into designated field in the related order.
        result = related_manager.for_order(order_instance).aggregate(total=Sum("value"))
        total = result['total'] if result['total'] is not None else Decimal('0.00')
        setattr(order_instance, field, total)
        order_instance.save(update_fields=[field])

    @staticmethod
    def update_order_balance(order, included_fields):
        order.total_price = Decimal('0.00')
        order.balance = Decimal('0.00')

        # Calculate order total price.
        for field in included_fields:
            if field != "paid":
                order.total_price += getattr(order, field)

        # Calculate order balance
        order.balance = order.paid - order.total_price

        order.save(update_fields=["total_price", "balance"])
