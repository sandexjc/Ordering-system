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
        for field_name in ['ordered', 'delivered', 'cutted', 'edged']:
            self.set_lg_checkbox(field_name)
        self.set_readonly('material')
        self.fields['material'].required = False
        self.fields['manufacturer'].required = False


# Formset for managing progress for multiple plates linked to a single order

PlateProgressFormSet = inlineformset_factory(
    parent_model = Order,
    model = Plate,
    form = PlateProgressForm,
    extra = 0,
    can_delete = False,
)