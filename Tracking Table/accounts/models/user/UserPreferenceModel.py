from django.conf import settings
from django.db import models


THEME_LIGHT = "light"
THEME_DARK = "dark"

THEME_CHOICES = (
    (THEME_LIGHT, "Светла"),
    (THEME_DARK, "Тъмна"),
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

    def __str__(self):
        return "Appearance for %s" % self.user_id

    @classmethod
    def theme_for(cls, user):
        if not getattr(user, "is_authenticated", False):
            return THEME_LIGHT
        theme = cls.objects.filter(pk=user.pk).values_list("theme", flat=True).first()
        if theme in (THEME_LIGHT, THEME_DARK):
            return theme
        return THEME_LIGHT
