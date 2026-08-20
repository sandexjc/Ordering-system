from .EditVitrineForm import EditVitrineForm
from vitrine.models import Vitrine


class VitrineOrderForm(EditVitrineForm):

    """

    Hierarchy:
    FormFieldsStyleMixin -> BaseModelForm -> VitrineForm -> EditVitrineForm -> VitrineOrderForm
    forms.ModelForm -> BaseModelForm -> VitrineForm -> EditVitrineForm -> VitrineOrderForm
    FormFieldsSetupMixin -> EditVitrineForm -> VitrineOrderForm

    Shared create/edit vitrine header for the dynamic modal.
    ID is a template-only readonly field on edit. created_date is editable on edit.

    --- Fields inherited from EditVitrineForm ---

    white_seal_type = forms.CharField(required=False)
    black_seal_type = forms.CharField(required=False)
    white_seal_total_value = forms.DecimalField(max_digits=10, decimal_places=2, required=False)
    black_seal_total_value = forms.DecimalField(max_digits=10, decimal_places=2, required=False)

    --- Fields inherited from FormFieldsSetupMixin ---

    No explicit class fields inherited.

    """

    class Meta:
        model = Vitrine
        fields = (
            "created_date",
            "owner",
            "telephone",
            "order_type",
            "vitrine_manual_seal",
            "white_seal_custom_amount",
            "black_seal_custom_amount",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if "created_date" in self.fields:
                self.fields["created_date"].label = "Дата"
        else:
            self.fields.pop("created_date", None)
