from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.urls import reverse
from table.models import Order, Plate, Edge
from table.forms import PlateProgressFormSet, EdgeProgressFormSet, OrderProgressForm

class ViewOrder(LoginRequiredMixin, TemplateView):
    template_name = 'table/order_details.html'

    def get_context_data(self, pk, **kwargs):
        context = super(ViewOrder, self).get_context_data(**kwargs)

        # Get order and related items
        order = Order.objects.get_by_id(pk)
        plates = Plate.objects.for_order(order).select_related("order_id")
        edges = Edge.objects.for_order(order).select_related("order_id")

        # Attach progress steps dynamically to each item to represent with progress bar
        # (step_name, active, disabled)
        # Plates
        for plate in plates:
            plate.plate_steps = [
                ("ordered", plate.ordered, plate.from_client),
                ("delivered", plate.delivered, False),
                ("cutted", plate.cutted, order.client == "External"),
                ("edged", plate.edged, order.client == "External"),
            ]
        
        # Edges
        for edge in edges:
            edge.edge_steps = [
                ("ordered", edge.ordered, False),
                ("delivered", edge.delivered, False),
            ]
        
        # Order toolbar urls and targets
        edit_url = reverse("table:editOrder", kwargs={"pk": order.id})
        print_url = reverse("table:printOrder", kwargs={"pk": order.id})
        delete_target = f"modal-delete-{order.id}"
        progress_target = f"modal-progress-{order.id}"
        history_target = f"history-tab-{order.id}"
        refresh_option = True

        # Prepare context
        context.update({

            # Order and related items
            'order': order,
            'plates': plates,
            'edges': edges,

            # Forms
            'plate_forms': PlateProgressFormSet(instance=order, queryset=plates),
            'edge_forms': EdgeProgressFormSet(instance=order, queryset=edges),
            'order_progress': OrderProgressForm(instance=order),

            # Toolbar
            "toolbar_edit_url": edit_url,
            "toolbar_print_url": print_url,
            "toolbar_delete_target": delete_target,
            "toolbar_progress_target": progress_target,
            "toolbar_history_target": history_target,
            "toolbar_refresh_option": refresh_option,
        })

        return context
    
    def post(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())