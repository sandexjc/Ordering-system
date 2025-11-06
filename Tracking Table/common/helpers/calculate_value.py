from decimal import Decimal, ROUND_HALF_UP


def calculate_item_value(instance):
    qty = instance.quantity or Decimal('0')
    price = instance.price or Decimal('0')
    value = qty * price
    return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

