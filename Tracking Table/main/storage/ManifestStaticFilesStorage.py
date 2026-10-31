from django.conf import settings
from django.contrib.staticfiles.storage import (
    ManifestStaticFilesStorage as DjangoManifestStaticFilesStorage,
)


class ManifestStaticFilesStorage(DjangoManifestStaticFilesStorage):

    """

    Hierarchy:
    ManifestStaticFilesStorage -> Django ManifestStaticFilesStorage

    {% static %} uses the hashed name from staticfiles.json in development
    and in production. In DEBUG the manifest is read again on each URL so a
    new collectstatic is picked up without restarting the dev server.

    """

    def url(self, name, force=False):
        if settings.DEBUG:
            self.hashed_files, self.manifest_hash = self.load_manifest()
        return super().url(name, force=True)
