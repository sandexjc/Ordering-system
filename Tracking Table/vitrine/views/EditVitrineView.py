from common.views import BaseEditView
from vitrine import models
from vitrine import forms

class EditVitrine(BaseEditView):

    """ Main view for editing vitrine app specific orders. """

    model = models.Vitrine
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

            for form, item in zip(formset.forms, instances):

                # Save model formset items
                item.modified_by = user
                setattr(item, self.fk_field_name, self.object)
                item.save()

                # Handle extra (non-model) form fields
                if isinstance(item, models.Frame):
                    holes_count = form.cleaned_data.get("holes_count")
                    holes_position = form.cleaned_data.get("holes_position")
                    glass_type = form.cleaned_data.get("glass_type")

                    # HOLES
                    models.Hole.objects.update_or_create(
                        vitrine_id = item.vitrine_id,
                        frame_id=item,
                        defaults={
                            "holes_position": holes_position,
                            "quantity": holes_count,
                            "price": 2,
                        }
                    )

                    # GLASS
                    models.Glass.objects.update_or_create(
                        vitrine_id = item.vitrine_id,
                        frame_id=item,
                        defaults={
                            "glass_type": glass_type,
                            "quantity": (item.length * item.width) / 1000000,
                            "price": 0,
                            }
                    )

                    # SEAL
                    models.Seal.objects.update_or_create(
                        vitrine_id = item.vitrine_id,
                        frame_id=item,
                        defaults={
                            "seal_type": item.profile_type if item.profile_type == "Black" else "White",
                            "quantity": ((item.length * 2) + (item.width * 2)) / 1000,
                            "price": 1,
                            }
                    )

            # Handle deletes
            for item in formset.deleted_objects:
                if isinstance(item, models.Frame):
                    models.Hole.frame_objects.for_frame(item).soft_delete()
                    models.Glass.frame_objects.for_frame(item).soft_delete()
                    models.Seal.frame_objects.for_frame(item).soft_delete()
                item.soft_delete()

