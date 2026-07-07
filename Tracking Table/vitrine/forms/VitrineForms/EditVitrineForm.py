from decimal import Decimal
from django import forms
from django.conf import settings

from vitrine.forms import VitrineForm
from vitrine.models import Vitrine
from common.mixins import FormFieldsSetupMixin

class EditVitrineForm(FormFieldsSetupMixin, VitrineForm):

    white_seal_type = forms.CharField(required=False)
    black_seal_type = forms.CharField(required=False)
    white_seal_total_value = forms.DecimalField(max_digits=10, decimal_places=2, required=False)
    black_seal_total_value = forms.DecimalField(max_digits=10, decimal_places=2, required=False)
    
    class Meta:
        model = Vitrine
        fields = (
            "id",
            "created_date",
            "owner",
            "telephone",
            "vitrine_manual_seal",
            "white_seal_custom_amount",
            "black_seal_custom_amount",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Customer contact information fields setup
        self.setup_contact_fields()

        if not settings.DJANGO_FEATURES__MANUAL_SEAL:
            for field_name in (
                "vitrine_manual_seal",
                "white_seal_custom_amount",
                "black_seal_custom_amount",
                "white_seal_type",
                "black_seal_type",
                "white_seal_total_value",
                "black_seal_total_value",
            ):
                self.fields.pop(field_name, None)
            return

        self.fields["white_seal_type"].initial = "Бяло уплътнение"
        self.fields["black_seal_type"].initial = "Черно уплътнение"

        self.set_switch("vitrine_manual_seal")
        self.set_number("white_seal_custom_amount")
        self.set_number("black_seal_custom_amount")
        self.set_readonly("white_seal_type")
        self.set_readonly("black_seal_type")
        self.set_readonly("white_seal_total_value")
        self.set_readonly("black_seal_total_value")

        self._set_manual_seal_helpers()

    def _get_input_decimal(self, field_name, fallback):
        raw_value = self.data.get(self.add_prefix(field_name))

        if raw_value in (None, ""):
            return Decimal(fallback or "0")

        try:
            return Decimal(str(raw_value).replace(",", "."))
        except Exception:
            return Decimal(fallback or "0")

    def _set_manual_seal_helpers(self):
        vitrine = self.instance

        white_custom_amount = self._get_input_decimal("white_seal_custom_amount", vitrine.white_seal_custom_amount)
        black_custom_amount = self._get_input_decimal("black_seal_custom_amount", vitrine.black_seal_custom_amount)

        self.fields["white_seal_total_value"].initial = (white_custom_amount * vitrine.white_seal_price).quantize(Decimal("0.01"))
        self.fields["black_seal_total_value"].initial = (black_custom_amount * vitrine.black_seal_price).quantize(Decimal("0.01"))