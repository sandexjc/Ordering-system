from decimal import Decimal

from common.service import BaseWorkflow
from vitrine.mapping import MODEL_RNAME_MAP
from .VitrinePriceSetter import VitrinePriceSetter


class VitrineWorkflow(BaseWorkflow):

    @classmethod
    def pre_save(cls, vitrine):
        # Set Vitrine order prices
        VitrinePriceSetter(vitrine).set_prices()

    @classmethod
    def on_delete(cls, vitrine):
        # Delete all vitrine order related items
        for manager_name in MODEL_RNAME_MAP.values():
            related_manager = getattr(vitrine, manager_name)
            related_manager.for_order(vitrine).soft_delete()
