from .TableBaseForm import TableForm
from .TableBaseFormSet import CustomTableInlineFormSet
from table.models import Cutting, Order
from django.forms import inlineformset_factory

class AddCuttingForm(TableForm):

    class Meta:
        model = Cutting
        fields = ("cutting_type", "quantity", "price", "value")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_number("price")
        self.set_readonly("value")


# Formset for managing multiple Cuttings linked to a single Order

CuttingFormSet = inlineformset_factory(
    parent_model=Order,
    model=Cutting,
    formset=CustomTableInlineFormSet,
    form=AddCuttingForm,
    extra=3,
    can_delete_extra=False,
)