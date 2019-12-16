from logging import getLogger

from django.contrib import admin
from django.utils.html import format_html

from django_q.tasks import async_task

from .models import Document

log = getLogger(__name__)


class DocumentsAdminSite(admin.AdminSite):
    site_header = "Document Store"


admin_site = DocumentsAdminSite(name="documentsadmin")


class DocumentTagListFilter(admin.SimpleListFilter):
    title = "Tags"
    parameter_name = "tags"

    def lookups(self, request, model_admin):
        return sorted(
            {
                (y, y)
                for x in Document.objects.values_list("tags", flat=True).distinct()
                for y in x
            }
        ) + [("None", "(None)")]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        elif self.value() == "None":
            return queryset.filter(tags__len=0)
        else:
            return queryset.filter(tags__contains=[self.value()])


class DocumentAdmin(admin.ModelAdmin):
    list_display = ("imported", "file_thumbnail_img", "imported_ok", "tags")
    list_display_links = ("imported", "file_thumbnail_img")
    list_editable = ("imported_ok", "tags")
    list_filter = (
        "source",
        "imported_ok",
        "author",
        "ocr_status",
        DocumentTagListFilter,
    )
    date_hierarchy = "imported"
    readonly_fields = ("file_img",)
    search_fields = ("ocr_text", "author")
    actions = ["reset_ocr_status"]

    def file_thumbnail_img(self, document):
        if document.file_thumbnail:
            return format_html(
                """<img src="{}" style="max-height: 400px; max-width: 800px" />""",
                document.file_thumbnail.url,
            )

    file_thumbnail_img.short_description = "Thumbnail"

    def file_img(self, document):
        if document.file:
            return format_html(
                """<a href="{}"><img src="{}" style="max-width: 1000px" /></a>""",
                document.file.url,
                document.file.url,
            )

    file_img.short_description = "Full-size Image"

    def reset_ocr_status(self, request, queryset):
        count = queryset.update(ocr_status="new", ocr_job_id=None, ocr_text="")
        self.message_user(
            request,
            f"{count} document{' was' if count == 1 else 's were'} updated and will be OCRd shortly.",
        )
        async_task("django.core.management.call_command", "ocr_queue_jobs")

    reset_ocr_status.short_description = "Reset OCR status to ‘new’"


admin_site.register(Document, DocumentAdmin)
