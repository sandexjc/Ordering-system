from decimal import Decimal

from common.managers import BaseManager
from vitrine.querysets import VitrinePriceConfigQuerySet


class VitrinePriceConfigManager(BaseManager):

    def get_queryset(self):
        return VitrinePriceConfigQuerySet(self.model, using=self._db).active()

    def all_with_deleted(self):
        return VitrinePriceConfigQuerySet(self.model, using=self._db)

    def get_current(self):
        config = self.all_with_deleted().singleton().first()
        if config:
            if config.deleted_at is not None:
                config.deleted_at = None
                config.save(update_fields=["deleted_at"])
            return config

        return self.create(
            singleton_key=1,
            black_profile_price=Decimal("7.92"),
            matte_profile_price=Decimal("6.80"),
            inox_profile_price=Decimal("6.80"),
            white_seal_price=Decimal("0.51"),
            black_seal_price=Decimal("0.51"),
            add_hole_price=Decimal("1.02"),
            manufacturing_price=Decimal("30.68"),
        )
