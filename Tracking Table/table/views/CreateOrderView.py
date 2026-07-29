from common.views import BaseCreateView
from table.models import Change, Order
from table.forms import CreateOrderForm, AddNoteForm


class CreateOrder(BaseCreateView):

    """

    Hierarchy:
    LoginRequiredMixin -> CreateView -> BaseCreateView -> CreateOrder

    --- Fields inherited from BaseCreateView ---

    template_name = "common/components/new_order.html"
    form_class = None
    change_model = None
    note_form_class = None
    related_field_name = None
    change_what = None
    redirect_name = None

    """

    model = Order
    change_model = Change
    form_class = CreateOrderForm
    note_form_class = AddNoteForm
    related_field_name = "order_id"
    change_what = "Order"
    redirect_name = "table:editOrder"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["order_type"] = self.kwargs.get("order_type")
        return kwargs