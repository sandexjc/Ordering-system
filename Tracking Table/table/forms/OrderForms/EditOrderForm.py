from table.forms import TableForm
from table.models import Order
from common.mixins import FormFieldsSetupMixin

class EditOrderForm(FormFieldsSetupMixin, TableForm):
    
    class Meta:
        model = Order
        fields = ("id", "created_date", "owner", "client", "telephone")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["client"].label = "Поръчка/Оферта"

        # Customer contact information fields setup
        self.setup_contact_fields()