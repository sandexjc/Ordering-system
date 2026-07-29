from table.forms import TableForm
from table.models import Order
from common.mixins import FormFieldsSetupMixin

class EditOrderForm(FormFieldsSetupMixin, TableForm):

    """

    Hierarchy:
    FormFieldsStyleMixin -> BaseModelForm -> TableForm -> EditOrderForm
    forms.ModelForm -> BaseModelForm -> TableForm -> EditOrderForm
    FormFieldsSetupMixin -> EditOrderForm

    --- Fields inherited from TableForm ---

    No explicit class fields inherited.

    --- Fields inherited from FormFieldsSetupMixin ---

    No explicit class fields inherited.

    """

    class Meta:
        model = Order
        fields = ("id", "created_date", "owner", "order_type", "telephone")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["order_type"].label = "Поръчка/Оферта"

        # Customer contact information fields setup
        self.setup_contact_fields()