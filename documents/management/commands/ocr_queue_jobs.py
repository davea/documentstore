from datetime import timedelta
from logging import getLogger

import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django_q.tasks import schedule

from documents.models import Document

log = getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        schedule_fetch = False
        for document in Document.objects.filter(
            ocr_status="new", tags__contains=["ocr"], imported_ok=True
        ):
            enqueue_document(document)
            schedule_fetch = True
        if schedule_fetch:
            schedule(
                "django.core.management.call_command",
                "ocr_fetch_results",
                schedule_type="O",
                next_run=timezone.now() + timedelta(minutes=5),
            )


def enqueue_document(document):
    log.debug("Queuing document {} for OCR...".format(document.id))
    response = requests.post(
        "https://cloud-eu.ocrsdk.com/v2/processImage",
        data=document.file.read(),
        params={
            "language": "English",
            "exportFormat": "txt",
            "profile": "textExtraction",
        },
        auth=(settings.OCRSDK_APP_ID, settings.OCRSDK_PASSWORD),
    )

    if not response.ok:
        document.ocr_status = "failed"
        try:
            document.ocr_job_id = response.json()["error"]["code"]
        except (KeyError, TypeError, ValueError):
            pass
        log.warning(
            "Couldn't enqueue document {} for OCR: {}".format(
                document.id, document.ocr_job_id
            )
        )
        document.save()
        return

    status_map = {
        "Submitted": "pending",
        "Queued": "pending",
        "InProgress": "pending",
        "Completed": "pending",
        "ProcessingFailed": "failed",
        "Deleted": "failed",
        "NotEnoughCredits": "failed",
    }
    result = response.json()
    document.ocr_job_id = result["taskId"]
    document.ocr_status = status_map.get(result["status"])
    document.save()
    log.debug(
        "Document {} queued as task ID {}, status {}".format(
            document.id, document.ocr_job_id, document.ocr_status
        )
    )
