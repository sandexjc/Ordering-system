from django.conf import settings
from django.db import models


THEME_CHOICES = (
    ("light", "Светла"),
    ("dark", "Тъмна"),
)

BACKGROUND_CHOICES = (
    ("city", "Град"),
    ("plain", "Едноцветен"),
    ("warm_paper", "Топла хартия"),
    ("blue", "Синьо"),
    ("green", "Зелено"),
    ("sand", "Пясък"),
    ("slate", "Шисти"),
)

TEXT_SIZE_CHOICES = (
    ("small", "Малък"),
    ("medium", "Среден"),
    ("large", "Голям"),
)

ROW_DENSITY_CHOICES = (
    ("standard", "Стандартно"),
    ("compact", "Компактно"),
    ("dense", "Плътно"),
)

MOTION_CHOICES = (
    ("off", "Нормално"),
    ("reduce", "Намалено"),
)

ACCENT_CHOICES = (
    ("stone", "Сиво"),
    ("blue", "Синьо"),
    ("teal", "Тюркоаз"),
    ("sand", "Пясък"),
    ("indigo", "Индиго"),
    ("rose", "Розово"),
    ("orange", "Оранжево"),
    ("slate", "Шисти"),
    ("clear", "Прозрачен"),
)


class UserPreference(models.Model):

    """

    Hierarchy:
    models.Model -> UserPreference

    One appearance row for the logged-in account. The account is
    settings.AUTH_USER_MODEL, the same user Device.user points at.
    A missing row means the defaults. The row is created on save.

    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="appearance",
    )
    theme = models.CharField(
        max_length=16,
        choices=THEME_CHOICES,
        default="light",
    )
    background = models.CharField(
        max_length=16,
        choices=BACKGROUND_CHOICES,
        default="city",
    )
    accent = models.CharField(
        max_length=16,
        choices=ACCENT_CHOICES,
        default="stone",
    )
    text_size = models.CharField(
        max_length=16,
        choices=TEXT_SIZE_CHOICES,
        default="medium",
    )
    row_density = models.CharField(
        max_length=16,
        choices=ROW_DENSITY_CHOICES,
        default="standard",
    )
    reduced_motion = models.CharField(
        max_length=16,
        choices=MOTION_CHOICES,
        default="off",
    )

    def __str__(self):
        return "Appearance for %s" % self.user_id

    @classmethod
    def appearance_for(cls, user):
        values = {
            "theme": "light",
            "background": "city",
            "accent": "stone",
            "text_size": "medium",
            "row_density": "standard",
            "reduced_motion": "off",
        }
        if not getattr(user, "is_authenticated", False):
            return values
        row = cls.objects.filter(pk=user.pk).values(
            "theme", "background", "accent", "text_size", "row_density", "reduced_motion"
        ).first()
        if not row:
            return values
        if row["theme"] in dict(THEME_CHOICES):
            values["theme"] = row["theme"]
        if row["background"] in dict(BACKGROUND_CHOICES):
            values["background"] = row["background"]
        if row["accent"] in dict(ACCENT_CHOICES):
            values["accent"] = row["accent"]
        if row["text_size"] in dict(TEXT_SIZE_CHOICES):
            values["text_size"] = row["text_size"]
        if row["row_density"] in dict(ROW_DENSITY_CHOICES):
            values["row_density"] = row["row_density"]
        if row["reduced_motion"] in dict(MOTION_CHOICES):
            values["reduced_motion"] = row["reduced_motion"]
        return values

    @classmethod
    def theme_for(cls, user):
        return cls.appearance_for(user)["theme"]
