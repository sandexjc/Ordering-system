from decimal import Decimal
from django.utils import timezone

from common.service import CurrencyOperations


class VitrinePriceSetter:
    """Service class responsible for setting vitrine prices on creation."""

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

        currency = CurrencyOperations.get_currency(timezone.now().date())

        for field, price_bgn in self.CURRENT_PRICES.items():
            final_price = self._convert_price(price_bgn, currency)
            setattr(self.vitrine, field, final_price)

    @staticmethod
    def _convert_price(price_bgn: Decimal, currency: str) -> Decimal:
        if currency == "€":
            return CurrencyOperations.to_eur(price_bgn)
        return price_bgn
