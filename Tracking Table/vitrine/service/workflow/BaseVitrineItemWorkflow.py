from common.service import BaseWorkflow
from vitrine.service import VitrineTotals

class BaseVitrineItemWorkflow(BaseWorkflow):

    @staticmethod
    def workflow_get_or_create(manager, lookup, defaults):
        item, created = manager.get_or_create(**lookup, defaults=defaults)

        if not created:
            for field, value in defaults.items():
                setattr(item, field, value)

        item.run_workflow_save()
        return item


    @classmethod
    def after_commit(cls, instance):
        instance.refresh_from_db()
        VitrineTotals.update_total(instance)
