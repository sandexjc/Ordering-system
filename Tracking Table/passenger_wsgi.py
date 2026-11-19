"""Passenger entry point. Superhosting loads this file and calls `application`."""

import os
import sys

APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
os.environ["_ORDERING_WSGI_SERVER"] = "1"

from main.wsgi import application  # noqa: E402
