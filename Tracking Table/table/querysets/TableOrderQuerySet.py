from common.querysets import BaseOrderQuerySet

class TableOrderQuerySet(BaseOrderQuerySet):

    """ Table app domain level shared Order models queryset. """
    
    # Client type orders filtering
    def client_type(self, client_type):
        return self.filter(client=client_type)