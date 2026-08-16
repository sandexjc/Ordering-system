from common.views import BaseOrderFormModalView
from table.models import Change, Order
from table import forms


class OrderFormModal(BaseOrderFormModalView):

    """

    Hierarchy:
    DynamicFeatureFlagRequiredMixin -> BaseOrderFormModalView -> OrderFormModal
    LoginRequiredMixin -> BaseOrderFormModalView -> OrderFormModal
    View -> BaseOrderFormModalView -> OrderFormModal

    Table-app create/edit order form for the dynamic modal.

    --- Fields inherited from BaseOrderFormModalView ---

    http_method_names = ["get", "post"]
    model = None
    form_class = None
    note_form_class = None
    related_formsets = {}
    fk_field_name = None
    change_model = None
    change_what = None
    fragment_template_name = None
    rows_template_name = None
    rows_context_name = "orders"
    row_prefetch_related = ()
    create_url_name = None
    edit_url_name = None

    """

    model = Order
    form_class = forms.OrderForm
    note_form_class = forms.AddNoteForm
    change_model = Change
    change_what = "Order"
    fk_field_name = "order_id"
    fragment_template_name = "table/components/order_form_fragment.html"
    rows_template_name = "table/components/table_rows.html"
    row_prefetch_related = ("plates", "edges", "others", "notes")
    create_url_name = "table:orderForm"
    edit_url_name = "table:orderFormEdit"

    related_formsets = {
        "plate_forms": forms.PlateFormSet,
        "cutting_forms": forms.CuttingFormSet,
        "edge_forms": forms.EdgeFormSet,
        "edging_forms": forms.EdgingFormSet,
        "others_forms": forms.OthersFormSet,
        "payment_forms": forms.PaymentFormSet,
    }
