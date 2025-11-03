from table.models import Order
from table.forms import TableForm
from common.mixins import ContactFieldsMixin

class CreateOrderForm(ContactFieldsMixin, TableForm):

    class Meta:
        model = Order
        fields = ("owner", "telephone", "client")

    def __init__(self, *args, **kwargs):
        order_type = kwargs.pop('order_type', None)
        super().__init__(*args, **kwargs)

        self.fields['client'].initial = order_type
        self.fields["client"].label = "Поръчка/Оферта"

        # Shared client contact fields
        self.setup_contact_fields()