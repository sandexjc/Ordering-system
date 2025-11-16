from common.managers import BaseItemManager
from vitrine.querysets import VitrineFrameItemQuerySet


class VitrineFrameItemManager(BaseItemManager):

    """ Vitrine app manager for frame model related ( with FK )items. """

    def __get_queryset(self):
        return VitrineFrameItemQuerySet(self.model, using=self._db).active()

    # Return order related active only items by class
    def for_frame(self, frame):
        return self.__get_queryset().for_frame(frame)

    # Return order related active only items by id
    def for_frame_id(self, frame_id):
        return self.__get_queryset().for_frame_id(frame_id)