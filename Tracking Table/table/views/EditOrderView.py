from common.views import BaseEditView
from table.models import Order 
from table import forms

class EditOrder(BaseEditView):

    """ Main view for editing table app specific orders. """

    model = Order
    form_class = forms.EditOrderForm
    note_form_class = forms.AddNoteForm
    template_name = 'table/edit_order.html'

    related_formsets = {
        "plate_forms": forms.PlateFormSet,
        "cutting_forms": forms.CuttingFormSet,
        "edge_forms": forms.EdgeFormSet,
        "edging_forms": forms.EdgingFormSet,
        "others_forms": forms.OthersFormSet,
        "payment_forms": forms.PaymentFormSet,
    }

    fk_field_name = "order_id"
    redirect_url = "table:editOrder"
