from django import forms

from vitrine.models import VitrinePriceConfig


class VitrinePriceConfigForm(forms.ModelForm):

    class Meta:
        model = VitrinePriceConfig
        fields = (
            "black_profile_price",
            "matte_profile_price",
            "inox_profile_price",
            "gold_profile_price",
            "white_seal_price",
            "black_seal_price",
            "add_hole_price",
            "manufacturing_price",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["black_profile_price"].label = "Черен профил (л.м.)"
        self.fields["matte_profile_price"].label = "Матов профил (л.м.)"
        self.fields["inox_profile_price"].label = "Инокс профил (л.м.)"
        self.fields["gold_profile_price"].label = "Златист профил (л.м.)"
        self.fields["white_seal_price"].label = "Бяло уплътнение (л.м.)"
        self.fields["black_seal_price"].label = "Черно уплътнение (л.м.)"
        self.fields["add_hole_price"].label = "Допълнителен отвор (1 бр.)"
        self.fields["manufacturing_price"].label = "Изработка (1 бр.)"

        for field in self.fields.values():
            field.widget.attrs.update(
                {
                    "class": "form-control",
                    "min": "0",
                    "step": "0.01",
                    "autocomplete": "off",
                }
            )
