from decimal import Decimal
from vitrine.service import BaseVitrineItemWorkflow
from vitrine.mapping import MODEL_RNAME_MAP


_PROFILE_PRICE_MAP = {
    "Black": "black_profile_price",
    "Matte": "matte_profile_price",
    "Inox": "inox_profile_price",
}

_SEAL_PRICE_MAP = {
    "Black": "black_seal_price",
    "White": "white_seal_price",
}


class FrameWorkflow(BaseVitrineItemWorkflow):

    @staticmethod
    def frame_perimeter(frame):
        # Return frame perimeter length in meters as Decimal.
        return (((frame.length * Decimal("2")) + (frame.width * Decimal("2"))) / Decimal("1000"))
    
    @staticmethod
    def frame_area(frame):
        # Return frame area in square meters as Decimal.
        return ((frame.length * frame.width) / Decimal("1000000"))

    @classmethod
    def pre_save(cls, frame):
        vitrine = frame.vitrine_id
        frame.price = getattr(vitrine, _PROFILE_PRICE_MAP[frame.profile_type])
        frame_length = cls.frame_perimeter(frame) * frame.quantity
        frame.value = cls.calculate_value(frame_length, frame.price)

    @classmethod
    def post_save(cls, frame):
        vitrine = frame.vitrine_id

        # --- SEAL --- #
        seal_type = frame.profile_type if frame.profile_type == "Black" else "White"
        seal_quantity = (cls.frame_perimeter(frame) * frame.quantity).quantize(Decimal("0.1"))
        seal_price = getattr(vitrine, _SEAL_PRICE_MAP[seal_type])
        seal_value = cls.calculate_value(seal_quantity, seal_price)

        cls.workflow_get_or_create(
            frame.seals,
            lookup={
                "vitrine_id": vitrine,
                "frame_id": frame,
            },
            defaults={
                "seal_type": seal_type,
                "quantity": seal_quantity,
                "price": seal_price,
                "value": seal_value,
            }
        )

        # --- HOLES --- #
        holes_count = (frame.holes_count - 2 if frame.holes_count > 2 else 0) * frame.quantity
        hole_price = getattr(vitrine, "add_hole_price")

        cls.workflow_get_or_create(
            frame.holes,
            lookup={
                "vitrine_id": vitrine,
                "frame_id": frame,
            },
            defaults={
                "holes_position": frame.holes_position,
                "quantity": holes_count,
                "price": hole_price,
                "value": cls.calculate_value(holes_count, hole_price),
            }
        )

        # --- GLASS --- #
        glass_quantity = (cls.frame_area(frame) * frame.quantity).quantize(Decimal("0.1"))
        glass_price = 0

        cls.workflow_get_or_create(
            frame.glasss,
            lookup={
                "vitrine_id": vitrine,
                "frame_id": frame,
            },
            defaults={
                "glass_type": frame.glass_type,
                "quantity": glass_quantity,
                "price": glass_price,
                "value": cls.calculate_value(glass_quantity, glass_price)
            }
        )

    @classmethod
    def on_delete(cls, frame):
        related_models = ("Hole", "Glass", "Seal")
        vitrine = frame.vitrine_id

        for model in related_models:
            manager_name = MODEL_RNAME_MAP.get(model)
            related_manager = getattr(vitrine, manager_name)
            for item in related_manager.for_order(vitrine).filter(frame_id=frame):
                item.run_workflow_delete()
