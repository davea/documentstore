import logging
from tempfile import TemporaryDirectory
import os
from hashlib import sha1

from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings

import doxieapi

from documents.models import Document

log = logging.getLogger(__name__)

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        log.debug("Searching for scanners:")
        scans_to_delete = []
        for scanner in doxieapi.DoxieScanner.discover():
            log.debug(scanner.name)
            for scan in scanner.scans:
                if not Document.objects.filter(doxieapi_scan_json=scan).exists():
                    self.import_new_scan(scanner, scan)
                elif Document.objects.filter(doxieapi_scan_json=scan, imported_ok=True).exists():
                    log.debug("{} has been imported and marked as OK, will delete".format(scan['name']))
                    scans_to_delete.append(scan['name'])
                else:
                    log.debug("{} has already been imported but not yet marked as OK.".format(scan['name']))
        if scans_to_delete:
            if not settings.DEBUG:
                log.debug("Deleting {} scans...".format(len(scans_to_delete)))
                if scanner.delete_scans(scans_to_delete):
                    log.debug("...done.")
                else:
                    log.debug("...failed.")
            else:
                log.debug("Not deleting {} scans because DEBUG = True".format(len(scans_to_delete)))

    def import_new_scan(self, scanner, scan):
        log.debug("Attempting to import scan {}".format(scan['name']))
        with TemporaryDirectory() as tmppath:
            scanpath = scanner.download_scan(scan['name'], tmppath)
            log.debug("Saved to {}".format(scanpath))
            with open(scanpath, 'rb') as f:
                file = File(f)
                file.name = os.path.join("scans", scanner.name, os.path.basename(scanpath))
                filehash = sha1(file.read()).hexdigest()
                document = Document.objects.create(doxieapi_scan_json=scan, file=file, filehash=filehash, source=scanner.name)
            log.debug("Created Document id {} from {}".format(document.id, scan['name']))
        return True
