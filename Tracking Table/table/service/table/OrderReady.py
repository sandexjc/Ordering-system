def plates_make_order_ready(order):
    """True when every plate on the order is delivered, cutted, and edged.

    An order with no plates is treated as ready (same as an empty loop over plates).
    Plate is imported lazily so this module cannot circular-import table.models
    while models are still loading (they import table.service).
    """
    from table.models import Plate

    return not (
        Plate.objects.for_order(order)
        .exclude(delivered=True, cutted=True, edged=True)
        .exists()
    )
