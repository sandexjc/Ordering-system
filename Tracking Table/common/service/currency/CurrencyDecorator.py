from decimal import Decimal
from common.service.currency import CurrencyOperations


class CurrencyDecorator:

    """ Decorates context dictionaries with currency presentation data. """

    @staticmethod
    def apply(context: dict, order_date) -> dict:
        decorated = {}

        for key, value in context.items():
            decorated[key] = CurrencyDecorator._decorate_value(
                value, order_date
            )

        return decorated

    @staticmethod
    def _decorate_value(value, order_date):
        if isinstance(value, Decimal):
            return CurrencyOperations.present(value, order_date)

        if isinstance(value, dict):
            return {
                key: CurrencyDecorator._decorate_value(dictionary_value, order_date)
                for key, dictionary_value in value.items()
            }


        return value
