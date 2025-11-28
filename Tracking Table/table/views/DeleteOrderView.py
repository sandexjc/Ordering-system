from common.views import BaseDeleteView
from table.models import Order


class DeleteOrder(BaseDeleteView):

    """ Delete view dedicated to Table app. """
    
    model = Order
