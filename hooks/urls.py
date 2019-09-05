from django.urls import re_path

from .views import dropbox_hook

app_name = "hooks"
urlpatterns = [re_path(r"^dropbox/?$", dropbox_hook, name="dropbox")]
