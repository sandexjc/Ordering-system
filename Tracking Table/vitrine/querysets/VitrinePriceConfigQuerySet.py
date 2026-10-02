from common.querysets import BaseQuerySet


class VitrinePriceConfigQuerySet(BaseQuerySet):

    # Return singleton config row if it exists.
    def singleton(self):
        return self.filter(singleton_key=1).order_by("pk")
