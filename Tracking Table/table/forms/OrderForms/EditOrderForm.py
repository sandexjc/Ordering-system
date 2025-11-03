from table.forms import TableForm
from table.models import Order
from common.mixins import ContactFieldsMixin

class EditOrderForm(ContactFieldsMixin, TableForm):
    
    class Meta:
        model = Order
        fields = ("id", "created_date", "owner", "client", "telephone")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["client"].label = "Поръчка/Оферта"

        # Shared client contact fields
        self.setup_contact_fields()