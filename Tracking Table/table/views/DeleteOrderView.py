from common.views import BaseDeleteView
from table.models import Change, Order


class DeleteOrder(BaseDeleteView):

    """

    Hierarchy:
    LoginRequiredMixin -> SingleObjectMixin -> View -> BaseDeleteView -> DeleteOrder

    --- Fields inherited from BaseDeleteView ---

    model = None
    http_method_names = ["post"]

    """
    
    model = Order
    change_model = Change
    fk_field_name = "order_id"
