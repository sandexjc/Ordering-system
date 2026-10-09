from common.db import unicode_contains
from common.querysets import BaseOrderQuerySet


class VitrineOrderQuerySet(BaseOrderQuerySet):

    """
    Vitrine app domain level shared Vitrine models queryset.

    Hierarchy:
    models.QuerySet
        \
         -> BaseQuerySet -> BaseOrderQuerySet -> VitrineOrderQuerySet

    --- Fields inherited from BaseOrderQuerySet ---

    No explicit class fields inherited.

    """

    def order_type(self, order_type):
        return self.filter(order_type=order_type)

    # Partial match across vitrine + related item text fields
    def search_contains(self, query):
        term = (query or "").strip()
        if len(term) < 2:
            return self

        return self.filter(
            self.pk_exact(term)
            | unicode_contains("owner", term)
            | unicode_contains("telephone", term)
            | self.related_text_exists("frames", term, "profile_type", "glass_type")
            | self.related_text_exists("notes", term, "content")
            | self.related_text_exists("others", term, "description")
        )
