from django.urls import path

from .views import dropbox_hook

app_name = "hooks"
urlpatterns = [path("dropbox", dropbox_hook)]
