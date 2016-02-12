from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.functional import cached_property

from .models import Document

class DocumentListView(LoginRequiredMixin, ListView):
    model = Document

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user, tags__contains=self.active_tags)

    @cached_property
    def all_tags(self):
        return sorted({y for x in Document.objects.values_list("tags", flat=True).distinct() for y in x})

    @cached_property
    def active_tags(self):
        return [t for t in self.request.GET.get('tags', '').split(',') if t]
