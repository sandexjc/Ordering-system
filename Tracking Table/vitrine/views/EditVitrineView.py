from common.views import BaseEditView
from vitrine.models import Vitrine, Frame, Hole, Seal
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

    # Helpers
    def __profile_quantity(self, frames, color):
        # Returns calculated total profile length based on frame dimenssions
        return sum((((frame.length * 2) + (frame.width * 2)) / 1000) * frame.quantity 
                   for frame in frames if frame.profile_type == color)

    def __formated_string(self, value, digits):
        # Returns formated string from value
        return f"{value:.{digits}f}"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get vitrine related items
        all_frames = Frame.objects.for_order(self.object)
        all_holes = Hole.objects.for_order(self.object)
        all_seal = Seal.objects.for_order(self.object)

        black_profile_length = self.__profile_quantity(all_frames, "Black")
        matte_profile_length = self.__profile_quantity(all_frames, "Matte")
        inox_profile_length = self.__profile_quantity(all_frames, "Inox")
        total_frame_count = sum(frame.quantity for frame in all_frames)

        white_seal_quantity = sum(seal.quantity for seal in all_seal if seal.seal_type == "White")
        black_seal_quantity = sum(seal.quantity for seal in all_seal if seal.seal_type == "Black")

        additional_total = self.object.manufacturing_total + self.object.holes_total

        # FIXME price - move prices into configurable model
        black_profile_price = 15.60
        matte_profile_price = 16
        inox_profile_price = 17
        additional_hole_price = 2
        seal_price = 1
        frame_manufactoring_price = 60

        context.update({

            # Frames
            "black_profile_length": self.__formated_string(black_profile_length, 2),
            "matte_profile_length": self.__formated_string(matte_profile_length, 2),
            "inox_profile_length": self.__formated_string(inox_profile_length, 2),

            "black_profile_price": self.__formated_string(black_profile_price, 2),
            "matte_profile_price": self.__formated_string(matte_profile_price, 2),
            "inox_profile_price": self.__formated_string(inox_profile_price, 2),

            "black_profile_total": self.__formated_string(black_profile_length * black_profile_price, 2),
            "matte_profile_total": self.__formated_string(matte_profile_length * matte_profile_price, 2),
            "inox_profile_total": self.__formated_string(inox_profile_length * inox_profile_price, 2),

            # Seal
            "white_seal": self.__formated_string(white_seal_quantity, 2),
            "black_seal": self.__formated_string(black_seal_quantity, 2),

            "seal_price": seal_price,

            "white_seal_total": self.__formated_string(white_seal_quantity * seal_price, 2),
            "black_seal_total": self.__formated_string(black_seal_quantity * seal_price, 2),

            # Additional
            "total_frames_count": self.__formated_string(total_frame_count, 0),
            "frame_manufactoring_price": self.__formated_string(frame_manufactoring_price, 2),

            "additional_holes": self.__formated_string(sum(hole.quantity for hole in all_holes), 0),
            "additional_hole_price": self.__formated_string(additional_hole_price, 2),

            "additional_total": self.__formated_string(additional_total, 2),

        })

        return context
