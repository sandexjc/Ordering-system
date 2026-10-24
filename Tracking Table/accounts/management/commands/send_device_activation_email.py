from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.http import HttpRequest

from accounts.helpers.devices.send_device_activation_email import send_device_activation_email
from common.middleware.CanonicalHostMiddleware import public_site_host


class Command(BaseCommand):

    """

    Email one device-activation link. The link is the same one the profile
    and the user list send. Opening it in a browser enrolls that browser.
    Old device cookies are left as they are.

    """

    help = "Email a device-activation link to one account, matched by username and email."

    def add_arguments(self, parser):
        parser.add_argument("username", help="Username of the account that should receive the link.")
        parser.add_argument("email", help="Email address of that same account.")

    def handle(self, *args, **options):
        if not settings.DJANGO_FEATURES__BROWSER_COOKIE_FILTER:
            self.stdout.write("Browser cookie filter is off. No email sent.")
            return

        email = options["email"].strip()
        user = get_user_model().objects.filter(
            username=options["username"],
            email__iexact=email,
        ).first()
        if user is None:
            self.stdout.write("No user with that username and email. No email sent.")
            return

        host = public_site_host()
        if host is None:
            self.stdout.write("Site host is not configured. No email sent.")
            return

        request = HttpRequest()
        request.META["HTTP_HOST"] = host
        request.META["wsgi.url_scheme"] = "https" if settings.DJANGO_SECURITY_ENABLE else "http"
        if not send_device_activation_email(request, user):
            self.stdout.write("No email sent.")
            return
        self.stdout.write("Activation email sent to %s." % email)
