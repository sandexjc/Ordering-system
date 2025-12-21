from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone

from common.service import CurrencyOperations


class VitrinePriceSetter:

    """ Service class responsible for setting vitrine prices on creation. """

    # FIXME: move prices into a configurable model
    CURRENT_PRICES = {
        "black_profile_price": Decimal("15.50"),
        "matte_profile_price": Decimal("16.60"),
        "inox_profile_price": Decimal("17.70"),
        "white_seal_price": Decimal("1.00"),
        "black_seal_price": Decimal("1.00"),
        "add_hole_price": Decimal("2.00"),
        "manufacturing_price": Decimal("60.00"),
    }

    def __init__(self, vitrine):
        self.vitrine = vitrine

    def set_prices(self) -> None:
        # Set vitrine order prices upon creation.

        if self.vitrine.pk:
            return

        rate = self._get_rate()

        for field, price in self.CURRENT_PRICES.items():
            final_price = self._calculate_price(price, rate)
            setattr(self.vitrine, field, final_price)

    @staticmethod
    def _calculate_price(price: Decimal, rate: Decimal) -> Decimal:
        return (price / rate).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

    @classmethod
    def _get_rate(cls) -> Decimal:
        if timezone.now().year > 2025:
            return CurrencyOperations.BGN_TO_EUR
        return Decimal("1")
