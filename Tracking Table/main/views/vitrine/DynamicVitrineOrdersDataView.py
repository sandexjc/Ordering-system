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
