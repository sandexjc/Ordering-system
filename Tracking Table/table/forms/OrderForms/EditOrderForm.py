from table.forms import TableForm
from table.models import Order

class EditOrderForm(TableForm):
    
    class Meta:
        model = Order
        fields = ("id", "created_date", "owner", "client", "telephone")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["owner"].widget.attrs["placeholder"] = "Client Name"
        self.fields["owner"].label = "Име на клиент"
        self.fields["client"].label = "Поръчка/Оферта"