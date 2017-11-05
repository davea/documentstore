import os
from logging import getLogger

from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils.text import slugify

from PIL import Image

log = getLogger(__name__)

def document_file_upload_path(instance, filename):
    return get_document_upload_path(instance, filename, thumbnail=False)

def document_file_thumbnail_upload_path(instance, filename=None):
    if filename is None:
        filename = os.path.basename(instance.file.name)
    # Thumbnails are always JPEGs
    filename = ".".join(filename.split(".")[:-1] + ['jpg'])
    return get_document_upload_path(instance, filename, thumbnail=True)

def get_document_upload_path(instance, filename, thumbnail):
    username = instance.owner.username if instance.owner else "nobody"
    if instance.doxieapi_scan_json:
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
        os.path.basename(filename)
    ]
    if thumbnail:
        parts.insert(-1, "thumbnails")
    return os.path.join(*parts)


class Document(models.Model):
    # Fields describing the content of the document
    author = models.CharField(max_length=128, blank=True, null=True, help_text="Who wrote/sent/created this document")
    date = models.DateField(blank=True, null=True, help_text="The date printed on the document")
    time = models.TimeField(blank=True, null=True, help_text="The time printed on the document")
    page_number = models.IntegerField(default=1)
    other_pages = models.ManyToManyField('self', blank=True)
    tags = ArrayField(models.TextField(blank=True), default=list, blank=True)

    # Fields relating to the import and storage of the document
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL)
    source = models.CharField(max_length=128, default="Manually uploaded", help_text="How this document made its way into the system")
    imported = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to=document_file_upload_path)
    filehash = models.CharField(max_length=128, blank=True, null=True)
    file_thumbnail = models.ImageField(
        blank=True, null=True, upload_to=document_file_thumbnail_upload_path,
        height_field='file_thumbnail_height', width_field='file_thumbnail_width'
    )
    file_thumbnail_width = models.IntegerField(blank=True, null=True)
    file_thumbnail_height = models.IntegerField(blank=True, null=True)

    original_kept = models.BooleanField(default=True, help_text="Whether the original physical copy of this document has been kept")
    original_location = models.CharField(max_length=256, blank=True, null=True, help_text="Where the physical copy of this document is kept")

    # Fields specific to documents imported using doxieapi
    doxieapi_scan_json = JSONField(blank=True, null=True)
    imported_ok = models.BooleanField(default=False)

    class Meta:
        ordering = ('-imported', )

    def save(self, *args, **kwargs):
        self._generate_thumbnail()
        self.tags = sorted(self.tags)
        return super().save(*args, **kwargs)

    def _generate_thumbnail(self, force=False):
        if not force and (not self.file or self.file_thumbnail):
            # We don't need a thumbnail, or already have one
            return
        image_types = ['jpg', 'jpeg', 'png']
        if self.file.name.split(".")[-1].lower() not in image_types:
            # File isn't thumbnailable
            return
        try:
            image = Image.open(self.file)
            image.thumbnail((800, 800), Image.ANTIALIAS)
        except OSError:
            log.warning("_generate_thumbnail: Couldn't read image for Document#{} ({}).".format(self.id, self.file.name))
            return
        contentfile = ContentFile(b'')
        image.save(contentfile, 'jpeg')
        filepath = document_file_thumbnail_upload_path(self)
        self.file_thumbnail.save(filepath, contentfile, save=False)
