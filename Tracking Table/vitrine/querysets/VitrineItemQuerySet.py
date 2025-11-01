from common.querysets import BaseItemQuerySet

class VitrineItemQuerySet(BaseItemQuerySet):

    """ Vitrine app domain level queryset sharing common order related ( FK ) models logic. """

    # Get order specific items by object
    def for_vitrine(self, vitrine):
        return self.filter(vitrine_id=vitrine)

    # Get order specific items by object id
    def for_vitrine_id(self, id):
        return self.filter(vitrine_id=id)