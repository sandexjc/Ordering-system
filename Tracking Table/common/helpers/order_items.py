from django.db.models import Sum
from decimal import Decimal


def update_order_item_total(order, model, fields):

    # Compute related total value and add it into corresponding order field
    
    for field in fields:
        if field == "manufacturing_total":
            total = (
                (model.objects.for_order(order)
                .aggregate(total=Sum('quantity'))['total']
                or Decimal('0.00')) * 60
            )
            setattr(order, field, total)
            continue

        total = (
            model.objects.for_order(order)
            .aggregate(total=Sum('value'))['total']
            or Decimal('0.00')
        )
        setattr(order, field, total)
    
    # Save new field values
    order.save(update_fields=[
        *fields,
    ])