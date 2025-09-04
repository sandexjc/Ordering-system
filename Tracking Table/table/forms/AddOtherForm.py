from .TableBaseForm import TableForm
from .TableBaseFormSet import CustomTableInlineFormSet
from table.models import Other, Order
from django.forms import inlineformset_factory

class AddOtherForm(TableForm):

    class Meta:
        model = Other
        fields = ("description", "quantity", "price", "value")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_number("price")
        self.set_readonly("value")


# Formset for managing multiple Other items linked to a single Order

OthersFormSet = inlineformset_factory(
    parent_model=Order,
    model=Other,
    formset=CustomTableInlineFormSet,
    form=AddOtherForm,
    extra=3,
    can_delete_extra=False,
)