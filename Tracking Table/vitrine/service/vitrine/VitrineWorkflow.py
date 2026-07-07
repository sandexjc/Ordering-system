from common.service import BaseWorkflow
from vitrine.mapping import MODEL_RNAME_MAP
from .VitrinePriceSetter import VitrinePriceSetter
from .VitrineTotals import VitrineTotals


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

    @classmethod
    def after_commit(cls, vitrine):
        VitrineTotals.sync_seal_total(vitrine)
        included_fields = [
            "frames_total",
            "holes_total",
            "others_total",
            "seals_total",
            "glass_total",
            "paid",
            "manufacturing_total",
        ]
        VitrineTotals.update_order_balance(vitrine, included_fields)
