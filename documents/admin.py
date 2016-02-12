from logging import getLogger

from django.contrib import admin
from django.utils.html import format_html

from .models import Document

log = getLogger(__name__)

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('imported', 'file_thumbnail_img', 'author', 'imported_ok', 'tags')
    list_display_links = ('imported', 'file_thumbnail_img')
    list_editable = ('imported_ok', 'tags')
    list_filter = ('source', 'imported_ok', 'author', 'tags')
    date_hierarchy = 'imported'
    readonly_fields = ('file_img', )

    def file_thumbnail_img(self, document):
        if document.file_thumbnail:
            return format_html(
                """<img src="{}" style="max-height: 200px; max-width: 400px" />""",
                document.file_thumbnail.url
            )
    file_thumbnail_img.short_description = 'Thumbnail'

    def file_img(self, document):
        if document.file:
            return format_html(
                """<a href="{}"><img src="{}" style="max-width: 1000px" /></a>""",
                document.file.url, document.file.url
            )
    file_img.short_description = 'Full-size Image'

admin.site.register(Document, DocumentAdmin)
