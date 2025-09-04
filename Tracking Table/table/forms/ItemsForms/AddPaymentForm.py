from table.forms import TableForm, TableFormSet
from table.models import Payment, Order
from django.forms import inlineformset_factory

class AddPaymentForm(TableForm):

    class Meta:
        model = Payment
        fields = ("payment_method", "value")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["payment_method"].widget.attrs["class"] = "form-select form-select-sm"
        self.set_number("value")


# Formset for managing multiple Payments linked to a single Order

PaymentFormSet = inlineformset_factory(
    parent_model=Order,
    model=Payment,
    formset=TableFormSet,
    form=AddPaymentForm,
    extra=1,
    can_delete_extra=False,
)