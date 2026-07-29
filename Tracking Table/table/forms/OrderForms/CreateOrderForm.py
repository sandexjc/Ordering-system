from table.models import Order
from table.forms import TableForm
from common.mixins import FormFieldsSetupMixin

class CreateOrderForm(FormFieldsSetupMixin, TableForm):

    """

    Hierarchy:
    FormFieldsStyleMixin -> BaseModelForm -> TableForm -> CreateOrderForm
    forms.ModelForm -> BaseModelForm -> TableForm -> CreateOrderForm
    FormFieldsSetupMixin -> CreateOrderForm

    --- Fields inherited from TableForm ---

    No explicit class fields inherited.

    --- Fields inherited from FormFieldsSetupMixin ---

    No explicit class fields inherited.

    """

    class Meta:
        model = Order
        fields = ("owner", "telephone", "order_type")

    def __init__(self, *args, **kwargs):
        order_type = kwargs.pop('order_type', None)
        super().__init__(*args, **kwargs)

        # self.fields["order_type"].initial = order_type
        self.fields["order_type"].label = "Поръчка/Оферта"

        # Customer contact information fields setup
        self.setup_contact_fields()