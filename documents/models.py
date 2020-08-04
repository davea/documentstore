import os
from logging import getLogger

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils.text import slugify

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit

log = getLogger(__name__)


def document_file_upload_path(instance, filename):
    return get_document_upload_path(instance, filename, thumbnail=False)


def document_file_thumbnail_upload_path(instance, filename=None):
    if filename is None:
        filename = os.path.basename(instance.file.name)
    # Thumbnails are always JPEGs
    filename = ".".join(filename.split(".")[:-1] + ["jpg"])
    return get_document_upload_path(instance, filename, thumbnail=True)


def get_document_upload_path(instance, filename, thumbnail):
    username = instance.owner.username if instance.owner else "nobody"
    if instance.source_metadata:
        category = "scans"
    elif instance.source == Document._meta.get_field("source").default:
        category = "uploads"
    else:
        category = "imports"
    parts = [
        "document__file",
        username,
        category,
        slugify(instance.source),
        os.path.basename(filename),
    ]
    if thumbnail:
        parts.insert(-1, "thumbnails")
    return os.path.join(*parts)


class Document(models.Model):
    # Fields describing the content of the document
    author = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        help_text="Who wrote/sent/created this document",
    )
    date = models.DateField(
        blank=True, null=True, help_text="The date printed on the document"
    )
    time = models.TimeField(
        blank=True, null=True, help_text="The time printed on the document"
    )
    page_number = models.IntegerField(default=1)
    other_pages = models.ManyToManyField("self", blank=True)
    tags = ArrayField(models.TextField(blank=True), default=list, blank=True)

    # Fields relating to the import and storage of the document
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL
    )
    source = models.CharField(
        max_length=128,
        default="Manually uploaded",
        help_text="How this document made its way into the system",
    )
    imported = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to=document_file_upload_path)
    filehash = models.CharField(max_length=128, blank=True, null=True)
    original_kept = models.BooleanField(
        default=True,
        help_text="Whether the original physical copy of this document has been kept",
    )
    original_location = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        help_text="Where the physical copy of this document is kept",
    )

    # Fields relating to OCR/searching of this document
    ocr_status = models.CharField(
        max_length=16,
        choices=(
            ("new", "New"),
            ("pending", "Pending"),
            ("complete", "Complete"),
            ("failed", "Failed"),
        ),
        default="new",
    )
    ocr_job_id = models.CharField(max_length=128, blank=True, null=True)
    ocr_text = models.TextField(blank=True, default="")

    # Fields relating to the source metadata of this document
    source_metadata = models.JSONField(blank=True, null=True)
    imported_ok = models.BooleanField(default=False)

    file_thumbnail = ImageSpecField(
        source="file",
        processors=[ResizeToFit(800, 800)],
        format="JPEG",
        options={"quality": 60},
    )

    class Meta:
        ordering = ("-imported",)

    def save(self, *args, **kwargs):
        self.tags = sorted(self.tags)
        return super().save(*args, **kwargs)
