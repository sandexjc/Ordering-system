from django.db.models import Sum
from decimal import Decimal


def calculate_order_totals(instance, related):

    """ Recalculate all totals for a given order using model managers. """

    # Reset summary fields
    instance.total_price = Decimal('0.00')
    instance.balance = Decimal('0.00')

    # Compute all related totals
    for field, model in related.items():
        total = (
            model.objects.for_order(instance)
            .aggregate(total=Sum('value'))['total']
            or Decimal('0.00')
        )
        setattr(instance, field, total)

        # Only add non-payment fields to total price
        if field != 'paid':
            instance.total_price += total

    # Compute balance
    instance.balance = instance.paid - instance.total_price

    # Save only affected fields
    instance.save(update_fields=[
        *related.keys(),
        'total_price',
        'balance',
    ])
