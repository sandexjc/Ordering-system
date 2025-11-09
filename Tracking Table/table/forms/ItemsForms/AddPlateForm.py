from table.forms import TableForm, TableFormSet
from table.models import Plate, Order
from django.forms import inlineformset_factory

class AddPlateForm(TableForm):

    class Meta:
        model = Plate
        fields = ("material", "manufacturer", "from_client", "quantity", "price", "value")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_sm_dropdown("manufacturer")
        self.set_switch("from_client")
        self.set_number("price")
        self.set_readonly("value")


# Formset for managing multiple Plates linked to a single Order

PlateFormSet = inlineformset_factory(
    parent_model=Order,
    model=Plate,
    formset=TableFormSet,
    form=AddPlateForm,
    extra=3,
    can_delete_extra=False,
)