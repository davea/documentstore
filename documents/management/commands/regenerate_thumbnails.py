import logging

from django.core.management.base import BaseCommand, CommandError

from documents.models import Document

log = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for document in Document.objects.filter(file__isnull=False):
            document._generate_thumbnail(force=True)
            document.save()

