from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone

from vitrine.models import Vitrine

_BGN_TO_EUR = Decimal("1.95583")

# FIXME prices - move prices into configurable model
_CURRENT_PRICES = {
    "black_profile_price": Decimal("15.50"),
    "matte_profile_price": Decimal("16.60"),
    "inox_profile_price": Decimal("17.70"),
    "white_seal_price": Decimal("1.00"),
    "black_seal_price": Decimal("1.00"),
    "add_hole_price": Decimal("2.00"),
    "manufacturing_price": Decimal("60.00"),
}


def set_vitrine_prices(vitrine: Vitrine):

    """ Set vitrine order prices upon creation. """

    if vitrine.pk:
        return

    rate = Decimal("1")
    if timezone.now().year > 2025:
        rate = _BGN_TO_EUR

    for field, price in _CURRENT_PRICES.items():
        final_price = (price / rate).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )
        setattr(vitrine, field, final_price)
