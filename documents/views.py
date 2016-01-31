from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Document

class DocumentListView(LoginRequiredMixin, ListView):
    model = Document

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)
