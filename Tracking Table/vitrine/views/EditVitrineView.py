from common.views import BaseEditView
from vitrine.service import VitrineContextBuilder
from vitrine.models import Vitrine
from vitrine import forms

class EditVitrine(BaseEditView):

    """ Main view for editing vitrine app specific orders. """

    model = Vitrine
    form_class = forms.EditVitrineForm
    note_form_class = forms.AddNoteForm
    template_name = 'vitrine/edit_vitrine.html'

    related_formsets = {
        "frame_forms": forms.FrameFormSet,
        "others_forms": forms.OthersFormSet,
        "payment_forms": forms.PaymentFormSet,
    }

    fk_field_name = "vitrine_id"
    redirect_url = "vitrine:edit_vitrine"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vitrine = self.object
        
        context.update(VitrineContextBuilder.build(vitrine))
        return context
