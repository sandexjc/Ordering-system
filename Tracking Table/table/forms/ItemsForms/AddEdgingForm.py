from table.forms import TableForm, TableFormSet
from table.models import Edging, Order
from django.forms import inlineformset_factory

class AddEdgingForm(TableForm):

    """

    Hierarchy:
    FormFieldsStyleMixin -> BaseModelForm -> TableForm -> AddEdgingForm
    forms.ModelForm -> BaseModelForm -> TableForm -> AddEdgingForm

    --- Fields inherited from TableForm ---

    No explicit class fields inherited.

    """

    class Meta:
        model = Edging
        fields = ("edging_type", "quantity", "price", "value")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_number("price")
        self.set_readonly("value")


# Formset for managing multiple Edgings linked to a single Order

EdgingFormSet = inlineformset_factory(
    parent_model=Order,
    model=Edging,
    formset=TableFormSet,
    form=AddEdgingForm,
    extra=3,
    can_delete_extra=False,
)