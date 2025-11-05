from common.views import BaseCreateView
from table.models import Change, Order
from table.forms import CreateOrderForm, AddNoteForm


class CreateOrder(BaseCreateView):

    model = Order
    change_model = Change
    form_class = CreateOrderForm
    note_form_class = AddNoteForm
    related_field_name = "order_id"
    change_what = "Order"
    redirect_name = "table:editOrder"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["order_type"] = self.kwargs.get("type")
        return kwargs