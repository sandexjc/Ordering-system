from common.db import unicode_contains
from common.querysets import BaseOrderQuerySet


class TableOrderQuerySet(BaseOrderQuerySet):

    """
    Table app domain level shared Order models queryset.

    Hierarchy:
    models.QuerySet
        \
         -> BaseQuerySet -> BaseOrderQuerySet -> TableOrderQuerySet

    --- Fields inherited from BaseOrderQuerySet ---

    No explicit class fields inherited.

    """

    # Order type filtering (order/offer)
    def order_type(self, order_type):
        return self.filter(order_type=order_type)

    # Partial match across order + related item text fields
    def search_contains(self, query):
        term = (query or "").strip()
        if len(term) < 2:
            return self

        return self.filter(
            self.pk_exact(term)
            | unicode_contains("owner", term)
            | unicode_contains("telephone", term)
            | self.related_text_exists("plates", term, "material")
            | self.related_text_exists("edges", term, "edge_type", "color_code")
            | self.related_text_exists("notes", term, "content")
            | self.related_text_exists("others", term, "description")
        )
