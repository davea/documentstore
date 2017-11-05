from django import template

from ..forms import DocumentTagsForm
from ..models import Document

register = template.Library()

@register.simple_tag(takes_context=True)
def querystring_for_tag(context, tag):
    """Returns the querystring used for the current request,
    but with the given tag toggled."""
    active_tags = set(context['view'].active_tags)

    if tag in active_tags:
        active_tags.remove(tag)
    elif tag == 'untagged':
        active_tags = {'untagged'}
    else:
        active_tags.add(tag)
        if 'untagged' in active_tags:
            active_tags.remove('untagged')

    query = context['request'].GET.copy()
    if active_tags:
        query['tags'] = ",".join(active_tags)
    elif 'tags' in query:
        query.pop('tags')
    return "?"+query.urlencode(safe=',')


@register.filter
def tags_form(document):
    """
    Returns a forms.DocumentTagsForm bound to the given Document
    """
    return DocumentTagsForm(instance=document)
