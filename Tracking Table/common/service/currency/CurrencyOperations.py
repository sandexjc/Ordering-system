from decimal import Decimal
from datetime import date

BGN_TO_EUR = Decimal("1.95583")
EURO_SWITCH_DATE = date(2026, 1, 1)

class CurrencyOperations:

    @staticmethod
    def to_eur(amount_bgn: Decimal) -> Decimal:
        return (amount_bgn / BGN_TO_EUR).quantize(Decimal("0.01"))

    @staticmethod
    def to_bgn(amount_eur: Decimal) -> Decimal:
        return (amount_eur * BGN_TO_EUR).quantize(Decimal("0.01"))
    
    @staticmethod
    def get_currency(order_date: date) -> str:
        # Returns currency symbol based on order created date
        return "€" if order_date > EURO_SWITCH_DATE else "лв"
