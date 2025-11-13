from vitrine.forms import VitrineForm, VitrineFormSet
from vitrine.models import Payment, Vitrine
from django.forms import inlineformset_factory

class AddPaymentForm(VitrineForm):

    class Meta:
        model = Payment
        fields = ("payment_method", "value")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_sm_dropdown("payment_method")
        self.set_number("value")


# Formset for managing multiple Payments linked to a single Vitrine.
PaymentFormSet = inlineformset_factory(
    parent_model=Vitrine,
    model=Payment,
    formset=VitrineFormSet,
    form=AddPaymentForm,
    extra=1,
    can_delete_extra=False,
)