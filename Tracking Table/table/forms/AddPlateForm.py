from .TableBaseForm import TableForm
from .TableBaseFormSet import CustomTableInlineFormSet
from table.models import Plate, Order
from django.forms import inlineformset_factory

class AddPlateForm(TableForm):

    class Meta:
        model = Plate
        fields = ("material", "manufacturer", "from_client", "quantity", "price", "value")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["manufacturer"].widget.attrs.update({
            "style": "background-color: #faf9f9",
            "class": "form-select form-select-sm",
        })
        self.set_switch("from_client")
        self.set_number("price")
        self.set_readonly("value")


# Formset for managing multiple Plates linked to a single Order

PlateFormSet = inlineformset_factory(
    parent_model=Order,
    model=Plate,
    formset=CustomTableInlineFormSet,
    form=AddPlateForm,
    extra=3,
    can_delete_extra=False,
)