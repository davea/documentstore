from django.conf.urls import url

from .views import DocumentListView, DocumentListViewAJAX

app_name = "documents"
urlpatterns = [
    url(r'^$', DocumentListView.as_view(), name="document_list"),
    url(r'^ajax$', DocumentListViewAJAX.as_view(), name="document_list_ajax"),
]
