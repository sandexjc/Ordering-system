from common.helpers import log_change


class BaseChangeSignalMixin:
    
    """ Base mixin for handling Change log creation in signals. """

    # Subclasses must define the below properties
    change_model = None
    fk_field_name = None
    related_item = None

    @classmethod
    def set_log_change(cls, related_instance, user, operation, old_state=None, new_state=None):

        # Logs a change using the configured model and field name.
        if not cls.change_model or not cls.fk_field_name:
            raise AttributeError(
                f"{cls.__name__} must define 'change_model' and 'related_field_name'."
            )

        log_change(
            ChangeModel=cls.change_model,
            fk_field_name=cls.fk_field_name,
            related_instance=related_instance,
            user=user,
            operation=operation,
            related_item=cls.related_item or related_instance.__class__.__name__,
            old_state=old_state,
            new_state=new_state,
        )
