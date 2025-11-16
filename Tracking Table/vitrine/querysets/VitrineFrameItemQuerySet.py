from common.querysets import BaseItemQuerySet

class VitrineFrameItemQuerySet(BaseItemQuerySet):

    """ Vitrine app queryset for frame model related ( with FK ) items. """

    # Get frame specific items by object
    def for_frame(self, frame):
        return self.filter(frame_id=frame)

    # Get frame specific items by object id
    def for_frame_id(self, frame_id):
        return self.filter(frame_id=frame_id)