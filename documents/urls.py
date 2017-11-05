from django.conf.urls import url

from .views import (
    DocumentListView, DocumentListViewAJAX, DocumentImportedOK,
    DocumentTagsEdit, DocumentImageRotate
)

app_name = "documents"
urlpatterns = [
    url(r'^$', DocumentListView.as_view(), name="document_list"),
    url(r'^ajax$', DocumentListViewAJAX.as_view(), name="document_list_ajax"),
    url(r'^(?P<pk>\d+)/imported_ok$', DocumentImportedOK.as_view(), name="document_imported_ok"),
    url(r'^(?P<pk>\d+)/tags_edit$', DocumentTagsEdit.as_view(), name="document_tags_edit"),
    url(r'^(?P<pk>\d+)/rotate/(?P<angle>\d+)$', DocumentImageRotate.as_view(), name="document_image_rotate"),
]
