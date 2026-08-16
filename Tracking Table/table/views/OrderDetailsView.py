from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.urls import reverse
from common.mixins import DynamicDetailsModeMixin
from table.models import Order, Plate, Edge
from table.forms import PlateProgressFormSet, EdgeProgressFormSet, OrderProgressForm

class ViewOrder(DynamicDetailsModeMixin, LoginRequiredMixin, TemplateView):

    """

    Hierarchy:
    DynamicDetailsModeMixin -> ViewOrder
    LoginRequiredMixin -> ViewOrder
    TemplateView -> ViewOrder

    Expanded order details HTML. Static `/table/` omits `?dynamic=1` and keeps
    the progress modal + formsets. Dynamic `/dynamic/` fetch adds `?dynamic=1`
    for click-to-toggle steps.

    --- Fields inherited from DynamicDetailsModeMixin ---

    progress_update_url_name = None

    --- Fields inherited from LoginRequiredMixin ---

    No explicit class fields inherited.

    --- Fields inherited from TemplateView ---

    No explicit class fields inherited.

    """

    template_name = 'table/order_details.html'
    progress_update_url_name = "table:update_progress"

    def get_context_data(self, pk, **kwargs):
        context = super(ViewOrder, self).get_context_data(**kwargs)

        # Get order and related items
        order = Order.objects.get_by_id(pk)
        plates = Plate.objects.for_order(order).select_related("order_id")
        edges = Edge.objects.for_order(order).select_related("order_id")

        # Attach type of the order related items
        # Attach progress steps dynamically to each item to represent with progress bar
        # (step_name, active, disabled)
        for plate in plates:
            plate.type = "plate"
            plate.plate_steps = [
                ("ordered", plate.ordered, plate.from_client),
                ("delivered", plate.delivered, False),
                ("cutted", plate.cutted, order.order_type == "offer"),
                ("edged", plate.edged, order.order_type == "offer"),
            ]
        
        # Edges
        for edge in edges:
            edge.type = "edge"
            edge.edge_steps = [
                ("ordered", edge.ordered, False),
                ("delivered", edge.delivered, False),
            ]

        order.type = "order"
        order.order_taken_steps = [
            ("order_taken", order.order_taken, False),
        ]
        order.invoice_steps = [
            ("invoice", order.invoice, False),
        ]
        
        # Order toolbar urls and targets
        edit_url = reverse("table:editOrder", kwargs={"pk": order.id})
        order_form_url = reverse("table:orderFormEdit", kwargs={"pk": order.id})
        print_url = reverse("table:printOrder", kwargs={"pk": order.id})
        delete_target = f"modal-delete-{order.id}"
        history_target = f"history-tab-{order.id}"
        refresh_option = True

        # Prepare context
        context.update({

            # Order and related items
            'order': order,
            'plates': plates,
            'edges': edges,

            # Toolbar
            "toolbar_edit_url": edit_url,
            "toolbar_order_form_url": order_form_url if self.is_dynamic_mode() else "",
            "toolbar_print_url": print_url,
            "toolbar_delete_target": delete_target,
            "toolbar_history_target": history_target,
            "toolbar_refresh_option": refresh_option,
        })

        dynamic_mode = self.add_dynamic_progress_context(context, order.id)
        if not dynamic_mode:
            # Static /table/: progress modal + UpdateOrder form POST (unchanged).
            context["plate_forms"] = PlateProgressFormSet(instance=order, queryset=plates)
            context["edge_forms"] = EdgeProgressFormSet(instance=order, queryset=edges)
            context["order_progress"] = OrderProgressForm(instance=order)
            context["toolbar_progress_target"] = f"modal-progress-{order.id}"

        return context
