from django.forms import modelform_factory
from .models import Document


DocumentTagsForm = modelform_factory(Document, fields=['tags'])
