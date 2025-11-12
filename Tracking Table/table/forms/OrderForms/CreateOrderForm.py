from table.models import Order
from table.forms import TableForm
from common.mixins import FormFieldsSetupMixin

class CreateOrderForm(FormFieldsSetupMixin, TableForm):

    class Meta:
        model = Order
        fields = ("owner", "telephone", "client")

    def __init__(self, *args, **kwargs):
        order_type = kwargs.pop('order_type', None)
        super().__init__(*args, **kwargs)

        self.fields['client'].initial = order_type
        self.fields["client"].label = "Поръчка/Оферта"

        # Customer contact information fields setup
        self.setup_contact_fields()