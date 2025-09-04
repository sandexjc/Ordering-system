from table.forms import TableForm
from table.models import Order

class OrderProgressForm(TableForm):
    
    # Form for updating the overall order progress (order taken, invoice).

    class Meta:
        model = Order
        fields = ('order_taken', 'invoice')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ['order_taken', 'invoice']:
            self.fields[field_name].widget.attrs.update({
                'style': 'width: 90px; height: 30px; margin-left: auto; margin-right: auto;',
                'class': 'form-check-input',
                'role': 'checkbox',
            })