from main.views.base import DynamicView
from table.models import Order


class DynamicTableOrdersData(DynamicView):

    """
    Dynamic endpoint for table order rows.

    Hierarchy:
    LoginRequiredMixin
            \
             -> MainView -> DynamicView -> DynamicTableOrdersData
            /
    TemplateView

    """

    model = Order
    rows_template_name = "table/components/table_rows.html"
