from django.conf.urls import url

from .views import DocumentListView, DocumentListViewAJAX, DocumentImportedOK

app_name = "documents"
urlpatterns = [
    url(r'^$', DocumentListView.as_view(), name="document_list"),
    url(r'^ajax$', DocumentListViewAJAX.as_view(), name="document_list_ajax"),
    url(r'^(?P<pk>\d+)/imported_ok$', DocumentImportedOK.as_view(), name="document_imported_ok"),
]
