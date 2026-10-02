from decimal import Decimal
from django.apps import apps
from django.utils import timezone

from common.service import CurrencyOperations


class VitrinePriceSetter:
    """Service class responsible for setting vitrine prices on creation."""

    PRICE_FIELDS = (
        "black_profile_price",
        "matte_profile_price",
        "inox_profile_price",
        "white_seal_price",
        "black_seal_price",
        "add_hole_price",
        "manufacturing_price",
    )

    def __init__(self, vitrine):
        self.vitrine = vitrine

    def set_prices(self) -> None:
        # Set vitrine order prices upon creation.
        if self.vitrine.pk:
            return

        currency = CurrencyOperations.get_currency(timezone.now().date())
        price_config = self._get_price_config()

        for field in self.PRICE_FIELDS:
            final_price = self._convert_price(getattr(price_config, field), currency)
            setattr(self.vitrine, field, final_price)

    @staticmethod
    def _convert_price(price_eur: Decimal, currency: str) -> Decimal:
        if currency == "€":
            return price_eur
        return CurrencyOperations.to_bgn(price_eur)

    @staticmethod
    def _get_price_config():
        config_model = apps.get_model("vitrine", "VitrinePriceConfig")
        return config_model.objects.get_current()
