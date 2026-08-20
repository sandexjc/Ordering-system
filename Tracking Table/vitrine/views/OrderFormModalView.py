from django.conf import settings

from common.views import BaseOrderFormModalView
from vitrine.models import Change, Vitrine
from vitrine.service import VitrineContextBuilder
from vitrine import forms


class VitrineOrderFormModal(BaseOrderFormModalView):

    """

    Hierarchy:
    DynamicFeatureFlagRequiredMixin -> BaseOrderFormModalView -> VitrineOrderFormModal
    LoginRequiredMixin -> BaseOrderFormModalView -> VitrineOrderFormModal
    View -> BaseOrderFormModalView -> VitrineOrderFormModal

    Vitrine-app create/edit order form for the dynamic modal.
    Extra context: auto/manual seal flags and VitrineContextBuilder totals.

    --- Fields inherited from BaseOrderFormModalView ---

    http_method_names = ["get", "post"]
    model = None
    form_class = None
    note_form_class = None
    related_formsets = {}
    fk_field_name = None
    change_model = None
    change_what = None
    fragment_template_name = None
    rows_template_name = None
    rows_context_name = "orders"
    row_prefetch_related = ()
    create_url_name = None
    edit_url_name = None

    """

    model = Vitrine
    form_class = forms.VitrineOrderForm
    note_form_class = forms.AddNoteForm
    change_model = Change
    change_what = "Vitrine"
    fk_field_name = "vitrine_id"
    fragment_template_name = "vitrine/components/order_form_fragment.html"
    rows_template_name = "vitrine/components/table_rows.html"
    row_prefetch_related = ("frames", "others", "notes")
    create_url_name = "vitrine:orderForm"
    edit_url_name = "vitrine:orderFormEdit"

    related_formsets = {
        "frame_forms": forms.FrameFormSet,
        "others_forms": forms.OthersFormSet,
        "payment_forms": forms.PaymentFormSet,
    }

    def get_extra_form_context(self):
        extra = {
            "feature_auto_seal_enabled": settings.DJANGO_FEATURES__AUTO_SEAL_SELECT,
            "feature_manual_seal_enabled": settings.DJANGO_FEATURES__MANUAL_SEAL,
        }
        extra.update(VitrineContextBuilder.build_context(self.object))
        return extra
