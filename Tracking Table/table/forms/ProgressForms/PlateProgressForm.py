from table.forms import TableForm
from table.models import Plate, Order
from django.forms import inlineformset_factory

class PlateProgressForm(TableForm):

    # Form for updating the progress of individual plates in an order.

    class Meta:
        model = Plate
        fields = ('ordered', 'delivered', 'cutted', 'edged', 'material', 'manufacturer')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        order = getattr(self.instance, "order_id", None)

        for field_name in ['ordered', 'delivered', 'cutted', 'edged']:
            self.set_lg_checkbox(field_name)

        self.set_readonly('material')
        self.set_not_required('material')
        self.set_not_required('manufacturer')

        # Disable 'ordered' field if plate is from a client
        self.disable_if(
            getattr(self.instance, "from_client", False),
            "ordered",
            reason="This plate should be supplied by the client and cannot be ordered."
        )

        # Disable 'cutted' and 'edged' fields in case order is offer
        if getattr(order, "client", None) == "External":
            self.disable_if(True, "cutted", reason="Cutting not applicable for offers.")
            self.disable_if(True, "edged", reason="Edging not applicable for offers.")


# Formset for managing progress for multiple plates linked to a single order
PlateProgressFormSet = inlineformset_factory(
    parent_model = Order,
    model = Plate,
    form = PlateProgressForm,
    extra = 0,
    can_delete = False,
)