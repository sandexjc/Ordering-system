from table.forms import TableForm
from table.models import Edge, Order
from django.forms import inlineformset_factory

class EdgeProgressForm(TableForm):

    # Form for updating the progress of individual edges in an order.

    class Meta:
        model = Edge
        fields = ('ordered', 'delivered', 'color_code', 'edge_type')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ['ordered', 'delivered']:
            self.set_sm_checkbox(field_name)
        for field_name in ['color_code', 'edge_type']:
            self.set_readonly(field_name)


# Formset for managing progress for multiple edges linked to a single order

EdgeProgressFormSet = inlineformset_factory(
    parent_model = Order,
    model = Edge,
    form = EdgeProgressForm,
    extra = 0,
    can_delete = False,
)