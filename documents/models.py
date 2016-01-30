from django.db import models
from django.contrib.postgres.fields import JSONField

# Using a function that simply returns the suggested filename allows us to
# specify its subdir via File().name.
def document_file_upload_path(instance, filename):
    return filename

class Document(models.Model):
    # Fields describing the content of the document
    author = models.CharField(max_length=128, blank=True, null=True, help_text="Who wrote/sent/created this document")
    date = models.DateField(blank=True, null=True, help_text="The date printed on the document")
    time = models.TimeField(blank=True, null=True, help_text="The time printed on the document")
    page_number = models.IntegerField(default=1)
    other_pages = models.ManyToManyField('self', blank=True)

    # Fields relating to the import and storage of the document
    source = models.CharField(max_length=128, default="Manually imported", help_text="How this document made its way into the system")
    imported = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to=document_file_upload_path)
    filehash = models.CharField(max_length=128, blank=True, null=True)
    original_kept = models.BooleanField(default=True, help_text="Whether the original physical copy of this document has been kept")
    original_location = models.CharField(max_length=256, blank=True, null=True, help_text="Where the physical copy of this document is kept")

    # Fields specific to documents imported using doxieapi
    doxieapi_scan_json = JSONField(blank=True, null=True)
    imported_ok = models.BooleanField(default=False)

    class Meta:
        ordering = ('-imported', )
