from django.conf import settings

from main.views.base import DynamicView
from vitrine.models import Vitrine


class DynamicVitrineOrdersData(DynamicView):

    """
    Dynamic endpoint for vitrine order rows.

    Hierarchy:
    LoginRequiredMixin
            \
             -> MainView -> DynamicView -> DynamicVitrineOrdersData
            /
    TemplateView

    """

    model = Vitrine
    rows_template_name = "vitrine/components/table_rows.html"
    rows_prefetch_related = ("frames", "others", "notes")

    @property
    def allowed_order_types(self):
        if settings.DJANGO_FEATURES__VITRINE_OFFERS:
            return ("order", "offer")
        return ("order",)
