from common.views import BaseEditView
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

    def _handle_formsets(self, formsets, user):

        for formset in formsets.values():
            instances = formset.save(commit=False)
            for item in instances:
                # create/update frame records
                item.modified_by = user
                setattr(item, self.fk_field_name, self.object)
                item.save()

                # create/update holes record

                # create/update glass records

                # create/update seal records


            for item in formset.deleted_objects:
                item.modified_by = user
                item.soft_delete()
