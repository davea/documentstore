from django.db import models
from django.contrib.postgres.fields import JSONField

class Document(models.Model):
    # Fields describing the content of the document
    author = models.CharField(max_length=128, blank=True, null=True, help_text="Who wrote/sent/created this document")
    date = models.DateField(blank=True, null=True, help_text="The date printed on the document")
    time = models.TimeField(blank=True, null=True, help_text="The time printed on the document")

    # Fields relating to the import and storage of the document
    source = models.CharField(max_length=128, default="Manually imported", help_text="How this document made its way into the system")
    imported = models.DateTimeField(auto_now_add=True)
    file = models.FileField()

    # Fields specific to documents imported using doxieapi
    doxieapi_scan_json = JSONField(blank=True, null=True)
    imported_ok = models.BooleanField(default=False)

