from main.views.base import BaseVitrineView


class VitrineOrders(BaseVitrineView):

    """
    Main view for displaying vitrine orders.

    Hierarchy:
    LoginRequiredMixin
            \
             -> MainView -> BaseVitrineView -> VitrineOrders
            /
    TemplateView

    --- Fields inherited from BaseVitrineView ---

    model = Vitrine
    template_name = "vitrine/vitrines.html"

    """

    order_type = "order"
    navigation = "vitrine"
