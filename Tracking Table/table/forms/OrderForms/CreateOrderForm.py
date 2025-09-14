from table.models import Order
from table.forms import TableForm

class CreateOrderForm(TableForm):

    class Meta:
        model = Order
        fields = ("owner", "telephone", "client")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["owner"].widget.attrs["placeholder"] = "Име на клиент"
        self.fields["owner"].label = "Име на клиент"
        self.fields["telephone"].widget.attrs["placeholder"] = "Телефон"
        self.fields["telephone"].label = "Телефон"
        self.fields["client"].label = "Поръчка/Оферта"