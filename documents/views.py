from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.functional import cached_property
from django.urls import reverse

from .models import Document
from .forms import DocumentTagsForm


class DocumentOwnerMixin(LoginRequiredMixin):
    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


class DocumentListView(DocumentOwnerMixin, ListView):
    model = Document
    paginate_by = 25

    def get_queryset(self):
        user_docs = super().get_queryset()
        if 'untagged' in self.active_tags:
            return user_docs.filter(tags__len=0)
        else:
            return user_docs.filter(tags__contains=self.active_tags)

    @cached_property
    def all_tags(self):
        return sorted({y for x in Document.objects.values_list("tags", flat=True).distinct() for y in x}) + ['untagged']

    @cached_property
    def active_tags(self):
        return [t for t in self.request.GET.get('tags', '').split(',') if t]


class DocumentListViewAJAX(DocumentListView):
    template_name = "documents/includes/list.html"


class DocumentImportedOK(DocumentOwnerMixin, DetailView):
    model = Document
    template_name = "documents/includes/imported_status_button.html"

    def post(self, request, *args, **kwargs):
        document = self.get_object()
        document.imported_ok = True
        document.save()
        return self.get(request, *args, **kwargs)


class DocumentTagsEdit(DocumentOwnerMixin, UpdateView):
    model = Document
    form_class = DocumentTagsForm
    template_name = "documents/includes/tags_form.html"

    def get_success_url(self):
        return reverse("documents:document_tags_edit", args=[self.object.id]) + "?saved"

    @property
    def saved(self):
        return 'saved' in self.request.GET
