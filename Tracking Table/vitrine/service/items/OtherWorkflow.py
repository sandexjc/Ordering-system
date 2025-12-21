from vitrine.service import BaseVitrineItemWorkflow


class OtherWorkflow(BaseVitrineItemWorkflow):

    @classmethod
    def pre_save(cls, other):
        other.value = cls.calculate_value(other.quantity, other.price)
