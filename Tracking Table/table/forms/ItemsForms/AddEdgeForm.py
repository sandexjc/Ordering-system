from table.forms import TableForm, TableFormSet
from table.models import Edge, Order
from django.forms import inlineformset_factory

class AddEdgeForm(TableForm):

    class Meta:
        model = Edge
        fields = ("edge_type", "color_code", "quantity", "price", "value", "visible")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_number("price")
        self.set_readonly("value")
        self.set_switch("visible")


# Formset for managing multiple Edges linked to a single Order

EdgeFormSet = inlineformset_factory(
    parent_model=Order,
    model=Edge,
    formset=TableFormSet,
    form=AddEdgeForm,
    extra=3,
    can_delete_extra=False,
)