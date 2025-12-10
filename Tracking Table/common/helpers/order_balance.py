# from django.db.models import Sum
from decimal import Decimal


def update_order_balance(order, included_fields):

    """ Recalculate total_price and balance for a given order. """

    # Reset summary fields
    order.total_price = Decimal('0.00')
    order.balance = Decimal('0.00')

    # Compute all related totals
    for field in included_fields:
        if field == "paid":
            continue
        order.total_price += getattr(order, field)
    
    # Compute balance
    order.balance = order.paid - order.total_price

    # Save computed values
    order.save(update_fields=[
        'total_price',
        'balance',
    ])
