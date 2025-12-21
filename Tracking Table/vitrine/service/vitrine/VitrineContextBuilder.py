from decimal import Decimal

class VitrineContextBuilder:

    """ Vitrine custom order information builder. """

    # --- Helpers --- #

    @staticmethod
    def _profile_qty(frames, color):
        return sum(
            (
                (((frame.length * 2) + (frame.width * 2)) / Decimal("1000"))
                * frame.quantity
                for frame in frames
                if frame.profile_type == color
            ),
            start=Decimal("0")
        )

    @staticmethod
    def _format(value, digits=2):
        return f"{value:.{digits}f}"

    # --- Formatting --- #
    
    @classmethod
    def _format_context(cls, context: dict) -> dict:
        formatted = {}

        for key, value in context.items():
            digits = 0 if key in ("total_frames_count", "additional_holes") else 2
            formatted[key] = cls._format(value, digits)

        return formatted
    
    # --- Base --- #

    @classmethod
    def _build_base_context(cls, vitrine):
        frames = vitrine.frames.for_order(vitrine)
        holes = vitrine.holes.for_order(vitrine)
        seals = vitrine.seals.for_order(vitrine)

        black_profile_len = cls._profile_qty(frames, "Black")
        matte_profile_len = cls._profile_qty(frames, "Matte")
        inox_profile_len = cls._profile_qty(frames, "Inox")

        white_seal_qty = sum(seal.quantity for seal in seals if seal.seal_type == "White")
        black_seal_qty = sum(seal.quantity for seal in seals if seal.seal_type == "Black")

        total_frames_count = sum(frame.quantity for frame in frames)
        additional_holes_count = sum(hole.quantity for hole in holes)
        additional_total = vitrine.manufacturing_total + vitrine.holes_total

        return {
            # Profile lengths
            "black_profile_len": black_profile_len,
            "matte_profile_len": matte_profile_len,
            "inox_profile_len": inox_profile_len,

            # Profile totals
            "black_profile_total": black_profile_len * vitrine.black_profile_price,
            "matte_profile_total": matte_profile_len * vitrine.matte_profile_price,
            "inox_profile_total": inox_profile_len * vitrine.inox_profile_price,

            # Seals
            "white_seal": white_seal_qty,
            "black_seal": black_seal_qty,
            "white_seal_total": white_seal_qty * vitrine.white_seal_price,
            "black_seal_total": black_seal_qty * vitrine.black_seal_price,

            # Additionals
            "total_frames_count": total_frames_count,
            "additional_holes": additional_holes_count,
            "additional_total": additional_total,
        }
    
    # --- Public API --- #

    @classmethod
    def build_context(cls, vitrine) -> dict:

        # Build context
        context = cls._build_base_context(vitrine)
        return cls._format_context(context)
