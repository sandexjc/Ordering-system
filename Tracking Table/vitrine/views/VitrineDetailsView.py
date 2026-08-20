from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.urls import reverse

from common.mixins import DynamicDetailsModeMixin
from vitrine.models import Vitrine
from vitrine.forms import VitrineProgressForm


class ViewVitrine(DynamicDetailsModeMixin, LoginRequiredMixin, TemplateView):

    """

    Hierarchy:
    DynamicDetailsModeMixin -> ViewVitrine
    LoginRequiredMixin -> ViewVitrine
    TemplateView -> ViewVitrine

    Expanded vitrine details HTML. Static `/vitrine/` omits `?dynamic=1` and
    keeps the progress modal. Dynamic `/dynamic/` fetch adds `?dynamic=1` for
    click-to-toggle order_ready / order_taken.

    --- Fields inherited from DynamicDetailsModeMixin ---

    progress_update_url_name = None

    --- Fields inherited from LoginRequiredMixin ---

    No explicit class fields inherited.

    --- Fields inherited from TemplateView ---

    No explicit class fields inherited.

    """

    template_name = 'vitrine/vitrine_details.html'
    progress_update_url_name = "vitrine:update_progress"

    def get_context_data(self, pk, **kwargs):
        context = super(ViewVitrine, self).get_context_data(**kwargs)

        # Get vitrine and related items
        vitrine = Vitrine.objects.get_by_id(pk)

        # Progress-bar ids use type "order" so shared JS can sync `.active`.
        vitrine.type = "order"
        vitrine.order_ready_steps = [
            ("order_ready", vitrine.order_ready, False),
        ]
        vitrine.order_taken_steps = [
            ("order_taken", vitrine.order_taken, not vitrine.order_ready),
        ]

        # Order toolbar urls and targets
        edit_url = reverse("vitrine:edit_vitrine", kwargs={"pk": vitrine.id})
        order_form_url = reverse("vitrine:orderFormEdit", kwargs={"pk": vitrine.id})
        print_url = reverse("vitrine:print_vitrine", kwargs={"pk": vitrine.id})
        delete_target = f"modal-delete-{vitrine.id}"
        refresh_option = True

        # Prepare context
        context.update({

            # Order and related items
            'vitrine': vitrine,

            # Toolbar
            "toolbar_edit_url": edit_url,
            "toolbar_order_form_url": order_form_url if self.is_dynamic_mode() else "",
            "toolbar_print_url": print_url,
            "toolbar_delete_target": delete_target,
            "toolbar_refresh_option": refresh_option,
        })

        dynamic_mode = self.add_dynamic_progress_context(context, vitrine.id)
        if not dynamic_mode:
            # Static /vitrine/: progress modal + UpdateVitrine form POST (unchanged).
            context["vitrine_progress_form"] = VitrineProgressForm(instance=vitrine)
            context["toolbar_progress_target"] = f"modal-progress-{vitrine.id}"

        return context
