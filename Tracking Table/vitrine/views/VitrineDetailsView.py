from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.urls import reverse

from vitrine.models import Vitrine
from vitrine.forms import VitrineProgressForm


class ViewVitrine(LoginRequiredMixin, TemplateView):
    template_name = 'vitrine/vitrine_details.html'

    def get_context_data(self, pk, **kwargs):
        context = super(ViewVitrine, self).get_context_data(**kwargs)

        # Get vitrine and related items
        vitrine = Vitrine.objects.get_by_id(pk)
        
        # Order toolbar urls and targets
        edit_url = reverse("vitrine:edit_vitrine", kwargs={"pk": vitrine.id})
        print_url = reverse("vitrine:print_vitrine", kwargs={"pk": vitrine.id})
        progress_target = f"modal-progress-{vitrine.id}"
        delete_target = f"modal-delete-{vitrine.id}"
        refresh_option = True

        # Prepare context
        context.update({

            # Order and related items
            'vitrine': vitrine,
            'vitrine_progress_form': VitrineProgressForm(instance=vitrine),

            # Toolbar
            "toolbar_edit_url": edit_url,
            "toolbar_print_url": print_url,
            "toolbar_progress_target": progress_target,
            "toolbar_delete_target": delete_target,
            "toolbar_refresh_option": refresh_option,
        })

        return context
    
    def post(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())