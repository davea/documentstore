from logging import getLogger

import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from documents.models import Document

log = getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        self.fetch_completed_tasks()
        self.fetch_individual_tasks()

    def fetch_completed_tasks(self):
        response = requests.get(
            "https://cloud-eu.ocrsdk.com/v2/listFinishedTasks",
            auth=(settings.OCRSDK_APP_ID, settings.OCRSDK_PASSWORD),
        ).json()
        if "tasks" not in response:
            return
        for task in response["tasks"]:
            self.update_document_from_task(task)

    def update_document_from_task(self, task):
        try:
            document = Document.objects.get(
                ocr_status="pending", ocr_job_id=task["taskId"]
            )
        except Document.DoesNotExist:
            log.debug("No pending document for {}".format(task["taskId"]))
            self.delete_finished_task(task["taskId"])
            return
        log.debug("Updating document {} with finished task".format(document.id))
        for url in task["resultUrls"]:
            r = requests.get(url)
            r.encoding = "utf-8"
            document.ocr_text += r.text
        document.ocr_status = "complete"
        document.save()
        self.delete_finished_task(task["taskId"])

    def delete_finished_task(self, task_id):
        response = requests.post(
            "https://cloud-eu.ocrsdk.com/v2/deleteTask",
            params={"taskId": task_id},
            auth=(settings.OCRSDK_APP_ID, settings.OCRSDK_PASSWORD),
        )

    @transaction.atomic
    def fetch_individual_tasks(self):
        for document in Document.objects.select_for_update().filter(
            ocr_status="pending", ocr_job_id__isnull=False, tags__contains=["ocr"]
        ):
            self.fetch_individual_task(document)

    def fetch_individual_task(self, document):
        log.debug("Fetching task for document {}".format(document.id))
        task = requests.get(
            "https://cloud-eu.ocrsdk.com/v2/getTaskStatus",
            params={"taskId": document.ocr_job_id},
            auth=(settings.OCRSDK_APP_ID, settings.OCRSDK_PASSWORD),
        ).json()
        if task["status"] == "Complete":
            self.update_document_from_task(task)
        else:
            log.debug(
                "Task status for document {} is {}".format(document.id, task["status"])
            )

