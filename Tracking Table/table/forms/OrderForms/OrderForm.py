from table.models import Order
from table.forms import TableForm
from common.mixins import FormFieldsSetupMixin


class OrderForm(FormFieldsSetupMixin, TableForm):

    """

    Hierarchy:
    FormFieldsStyleMixin -> BaseModelForm -> TableForm -> OrderForm
    forms.ModelForm -> BaseModelForm -> TableForm -> OrderForm
    FormFieldsSetupMixin -> OrderForm

    Shared create/edit order header for the dynamic modal.
    ID is a template-only readonly field on edit. created_date is editable on edit.

    --- Fields inherited from TableForm ---

    No explicit class fields inherited.

    --- Fields inherited from FormFieldsSetupMixin ---

    No explicit class fields inherited.

    """

    class Meta:
        model = Order
        fields = ("created_date", "owner", "telephone", "order_type")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["order_type"].label = "Поръчка/Оферта"
        self.setup_contact_fields()
        if self.instance and self.instance.pk:
            self.fields["created_date"].label = "Дата"
        else:
            self.fields.pop("created_date", None)
