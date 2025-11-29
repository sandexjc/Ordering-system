from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from vitrine.models import Vitrine

class PrintVitrine(LoginRequiredMixin, TemplateView):
    model = Vitrine
    template_name = 'vitrine/print_vitrine.html'
    
    def get_context_data(self, pk, **kwargs):
        context = super(PrintVitrine, self).get_context_data(**kwargs)
        context['vitrine'] = Vitrine.objects.get_by_id(pk)

        return context