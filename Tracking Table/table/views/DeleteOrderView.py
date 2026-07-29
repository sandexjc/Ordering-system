from common.views import BaseDeleteView
from table.models import Order


class DeleteOrder(BaseDeleteView):

    """

    Hierarchy:
    LoginRequiredMixin -> SingleObjectMixin -> View -> BaseDeleteView -> DeleteOrder

    --- Fields inherited from BaseDeleteView ---

    model = None

    """
    
    model = Order
