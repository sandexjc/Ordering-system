from django.conf import settings
from django.db import models


THEME_LIGHT = "light"
THEME_DARK = "dark"

THEME_CHOICES = (
    (THEME_LIGHT, "Светла"),
    (THEME_DARK, "Тъмна"),
)

BACKGROUND_CITY = "city"
BACKGROUND_PLAIN = "plain"
BACKGROUND_WARM_PAPER = "warm_paper"
BACKGROUND_BLUE = "blue"
BACKGROUND_GREEN = "green"
BACKGROUND_SAND = "sand"
BACKGROUND_SLATE = "slate"

BACKGROUND_CHOICES = (
    (BACKGROUND_CITY, "Град"),
    (BACKGROUND_PLAIN, "Едноцветен"),
    (BACKGROUND_WARM_PAPER, "Топла хартия"),
    (BACKGROUND_BLUE, "Синьо"),
    (BACKGROUND_GREEN, "Зелено"),
    (BACKGROUND_SAND, "Пясък"),
    (BACKGROUND_SLATE, "Шисти"),
)

_THEMES = (THEME_LIGHT, THEME_DARK)
_BACKGROUNDS = (
    BACKGROUND_CITY,
    BACKGROUND_PLAIN,
    BACKGROUND_WARM_PAPER,
    BACKGROUND_BLUE,
    BACKGROUND_GREEN,
    BACKGROUND_SAND,
    BACKGROUND_SLATE,
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
        default=THEME_LIGHT,
    )
    background = models.CharField(
        max_length=16,
        choices=BACKGROUND_CHOICES,
        default=BACKGROUND_CITY,
    )

    def __str__(self):
        return "Appearance for %s" % self.user_id

    @classmethod
    def appearance_for(cls, user):
        values = {
            "theme": THEME_LIGHT,
            "background": BACKGROUND_CITY,
        }
        if not getattr(user, "is_authenticated", False):
            return values
        row = cls.objects.filter(pk=user.pk).values("theme", "background").first()
        if not row:
            return values
        if row["theme"] in _THEMES:
            values["theme"] = row["theme"]
        if row["background"] in _BACKGROUNDS:
            values["background"] = row["background"]
        return values

    @classmethod
    def theme_for(cls, user):
        return cls.appearance_for(user)["theme"]
