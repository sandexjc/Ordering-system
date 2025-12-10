from vitrine.models import Frame, Hole, Seal

class VitrineContextBuilder:

    """ Vitrine custom order information builder. """

    # FIXME price - move prices into configurable model
    BLACK_PRICE = 15.60
    MATTE_PRICE = 16
    INOX_PRICE = 17
    HOLE_PRICE = 2
    SEAL_PRICE = 1
    FRAME_MAN_PRICE = 60

    @staticmethod
    def __profile_quantity(frames, color):
        return sum(
            (((frame.length * 2) + (frame.width * 2)) / 1000) * frame.quantity
            for frame in frames if frame.profile_type == color
        )

    @staticmethod
    def __formated_string(value, digits=2):
        return f"{value:.{digits}f}"

    @classmethod
    def build(cls, vitrine):
        frames = Frame.objects.for_order(vitrine)
        holes = Hole.objects.for_order(vitrine)
        seals = Seal.objects.for_order(vitrine)

        black_len = cls.__profile_quantity(frames, "Black")
        matte_len = cls.__profile_quantity(frames, "Matte")
        inox_len = cls.__profile_quantity(frames, "Inox")

        white_seal_qty = sum(seal.quantity for seal in seals if seal.seal_type == "White")
        black_seal_qty = sum(seal.quantity for seal in seals if seal.seal_type == "Black")

        total_frames = sum(frame.quantity for frame in frames)
        additional_total = vitrine.manufacturing_total + vitrine.holes_total

        return {
            # Frame lengths
            "black_profile_length": cls.__formated_string(black_len),
            "matte_profile_length": cls.__formated_string(matte_len),
            "inox_profile_length": cls.__formated_string(inox_len),

            # Prices
            "black_profile_price": cls.__formated_string(cls.BLACK_PRICE),
            "matte_profile_price": cls.__formated_string(cls.MATTE_PRICE),
            "inox_profile_price": cls.__formated_string(cls.INOX_PRICE),

            # Totals
            "black_profile_total": cls.__formated_string(black_len * cls.BLACK_PRICE),
            "matte_profile_total": cls.__formated_string(matte_len * cls.MATTE_PRICE),
            "inox_profile_total": cls.__formated_string(inox_len * cls.INOX_PRICE),

            # Seal
            "white_seal": cls.__formated_string(white_seal_qty),
            "black_seal": cls.__formated_string(black_seal_qty),
            "seal_price": cls.SEAL_PRICE,
            "white_seal_total": cls.__formated_string(white_seal_qty * cls.SEAL_PRICE),
            "black_seal_total": cls.__formated_string(black_seal_qty * cls.SEAL_PRICE),

            # Additional
            "total_frames_count": cls.__formated_string(total_frames, 0),
            "frame_manufactoring_price": cls.__formated_string(cls.FRAME_MAN_PRICE),
            "additional_holes": cls.__formated_string(sum(h.quantity for h in holes), 0),
            "additional_hole_price": cls.__formated_string(cls.HOLE_PRICE),
            "additional_total": cls.__formated_string(additional_total),
        }
