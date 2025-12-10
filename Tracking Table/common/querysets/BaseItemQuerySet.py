from .BaseQuerySet import BaseQuerySet

class BaseItemQuerySet(BaseQuerySet):

    """ Queryset designed to share common related items ( FK ) models logic between apps. """

    def soft_delete(self):
        # Queryset level soft delete method for all objects in the queryset.
        for object in self:
            object.soft_delete()