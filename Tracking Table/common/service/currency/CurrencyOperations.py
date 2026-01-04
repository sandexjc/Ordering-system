from decimal import Decimal, ROUND_HALF_UP
from datetime import date

class CurrencyOperations:

    BGN_TO_EUR = Decimal("1.95583")
    EURO_SWITCH_DATE = date(2026, 1, 1)

    @staticmethod
    def to_eur(amount_bgn: Decimal) -> Decimal:
        # Returns converted bgn to eur amount
        return (amount_bgn / CurrencyOperations.BGN_TO_EUR).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

    @staticmethod
    def to_bgn(amount_eur: Decimal) -> Decimal:
        # Returns converted euro to bgn amount
        return (amount_eur * CurrencyOperations.BGN_TO_EUR).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
    
    @staticmethod
    def get_currency(order_date: date) -> str:
        # Returns currency symbol based on order created date
        return "€" if order_date > CurrencyOperations.EURO_SWITCH_DATE else "лв"
