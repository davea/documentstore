from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.functional import cached_property

from .models import Document

class DocumentListView(LoginRequiredMixin, ListView):
    model = Document
    paginate_by = 25

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user, tags__contains=self.active_tags)

    @cached_property
    def all_tags(self):
        return sorted({y for x in Document.objects.values_list("tags", flat=True).distinct() for y in x})

    @cached_property
    def active_tags(self):
        return [t for t in self.request.GET.get('tags', '').split(',') if t]

class DocumentListViewAJAX(DocumentListView):
    template_name = "documents/includes/list.html"

class DocumentImportedOK(LoginRequiredMixin, DetailView):
    model = Document
    template_name = "documents/includes/imported_status_button.html"

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)

    def post(self, request, *args, **kwargs):
        document = self.get_object()
        document.imported_ok = True
        document.save()
        return self.get(request, *args, **kwargs)
