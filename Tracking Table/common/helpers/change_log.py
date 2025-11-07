
def log_change(ChangeModel, fk_field_name, related_instance,
               user, operation, related_item, old_state=None, new_state=None):
    
    print(f"🟦 log_change(): related_instance={related_instance!r}, new_state={new_state!r}")
    
    """ 
    Generic change logger for any app.
        - Model should be explicitly set
        - FK field name should be explicitly set
    """

    ChangeModel.objects.create(
        **{
            fk_field_name: related_instance,
            "user": getattr(user, "first_name", user) or "System",
            "operation": operation,
            "related_item": related_item,
            "current_state": old_state or "",
            "new_state": new_state or "",
        }
    )
