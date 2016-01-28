from django.contrib import admin

from .models import Document

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('imported', 'author', 'file', 'imported_ok')
    list_editable = ('imported_ok', )

admin.site.register(Document, DocumentAdmin)
