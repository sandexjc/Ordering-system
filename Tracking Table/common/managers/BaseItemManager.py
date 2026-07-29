from .BaseManager import BaseManager

class BaseItemManager(BaseManager):

    """
    Queryset manager designed to share common Order related items ( FK ) models logic between apps.

    Hierarchy:
    models.Manager
        \
         -> BaseManager -> BaseItemManager

    --- Fields inherited from BaseManager ---

    No explicit class fields inherited.

    """

    pass