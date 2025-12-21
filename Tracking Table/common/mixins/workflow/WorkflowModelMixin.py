from common.service import BaseWorkflow

class WorkflowModelMixin:
    
    """ Mixin for models to add workflow service. """

    workflow_service_class = BaseWorkflow

    def run_workflow_save(self):
        if not self.workflow_service_class:
            raise NotImplementedError(
                f"{self.__class__.__name__} must define workflow_service_class"
            )
        self.workflow_service_class.run_save_seq(self)

    def run_workflow_delete(self):
        if not self.workflow_service_class:
            raise NotImplementedError(
                f"{self.__class__.__name__} must define workflow_service_class"
            )
        self.workflow_service_class.run_delete_seq(self)
