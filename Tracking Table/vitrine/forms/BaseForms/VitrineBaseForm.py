from django.conf import settings

from common.forms import BaseModelForm

class VitrineForm(BaseModelForm):

    """

    Hierarchy:
    FormFieldsStyleMixin -> BaseModelForm -> VitrineForm
    forms.ModelForm -> BaseModelForm -> VitrineForm

    --- Fields inherited from BaseModelForm ---

    No explicit class fields inherited.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if settings.DJANGO_FEATURES__VITRINE_OFFERS:
            return
        order_type = self.fields.get("order_type")
        if order_type is None:
            return
        order_type.choices = [("order", "Поръчка")]
        order_type.initial = "order"
        self.initial["order_type"] = "order"