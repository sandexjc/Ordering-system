from table.models import Order
from table.forms import TableForm

class CreateOrderForm(TableForm):

    class Meta:
        model = Order
        fields = ("owner", "telephone", "client")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["owner"].widget.attrs["placeholder"] = "Name"
        self.fields["owner"].label = "Client Name"