import os

from django.conf import settings
from django.contrib.staticfiles.finders import BaseFinder, searched_locations
from django.core.exceptions import SuspiciousFileOperation
from django.utils._os import safe_join


class CollectedStaticFilesFinder(BaseFinder):

    """

    Hierarchy:
    CollectedStaticFilesFinder -> BaseFinder

    The dev server looks up hashed files in STATIC_ROOT. list() stays empty
    so collectstatic does not copy that directory back into itself.

    """

    def check(self, **kwargs):
        return []

    def find(self, path, all=False):
        matches = []
        location = self.find_location(path)
        if location:
            if not all:
                return location
            matches.append(location)
        return matches

    def find_location(self, path):
        root = settings.STATIC_ROOT
        if not root:
            return None
        root = str(root)
        if root not in searched_locations:
            searched_locations.append(root)
        try:
            match = safe_join(root, path)
        except SuspiciousFileOperation:
            return None
        if os.path.isfile(match):
            return match
        return None

    def list(self, ignore_patterns):
        return iter(())
