from common.querysets import BaseItemQuerySet

class VitrineFrameItemQuerySet(BaseItemQuerySet):

    """
    Vitrine app queryset for frame model related ( with FK ) items.

    Hierarchy:
    models.QuerySet
        \
         -> BaseQuerySet -> BaseItemQuerySet -> VitrineFrameItemQuerySet

    --- Fields inherited from BaseItemQuerySet ---

    No explicit class fields inherited.

    """

    # Get frame specific items by object
    def for_frame(self, frame):
        return self.filter(frame_id=frame)

    # Get frame specific items by object id
    def for_frame_id(self, frame_id):
        return self.filter(frame_id=frame_id)