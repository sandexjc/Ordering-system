from table.forms import TableForm
from table.models import Order

class OrderProgressForm(TableForm):

    """

    Hierarchy:
    FormFieldsStyleMixin -> BaseModelForm -> TableForm -> OrderProgressForm
    forms.ModelForm -> BaseModelForm -> TableForm -> OrderProgressForm

    --- Fields inherited from TableForm ---

    No explicit class fields inherited.

    """

    class Meta:
        model = Order
        fields = ('order_taken', 'invoice')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ['order_taken', 'invoice']:
            self.set_sm_checkbox(field_name)