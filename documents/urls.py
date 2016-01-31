from django.conf.urls import url

from .views import DocumentListView

app_name = "documents"
urlpatterns = [
    url(r'^$', DocumentListView.as_view(), name="document_list"),
]
