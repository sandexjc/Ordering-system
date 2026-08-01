from main.views.base import StaticView
from vitrine.models import Vitrine


class VitrineOrders(StaticView):

    """
    Main view for displaying vitrine orders.

    Hierarchy:
    LoginRequiredMixin
            \
             -> MainView -> StaticView -> VitrineOrders
            /
    TemplateView

    --- Fields inherited from StaticView ---

    model = Vitrine
    template_name = "vitrine/vitrines.html"

    """

    model = Vitrine
    template_name = "vitrine/vitrines.html"
    order_type = "order"
    navigation = "vitrine"
