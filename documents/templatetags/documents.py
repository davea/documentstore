from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def querystring_for_tag(context, tag):
    """Returns the querystring used for the current request,
    but with the given tag toggled."""
    active_tags = set(context['view'].active_tags)
    if tag in active_tags:
        active_tags.remove(tag)
    else:
        active_tags.add(tag)
    query = context['request'].GET.copy()
    if active_tags:
        query['tags'] = ",".join(active_tags)
    elif 'tags' in query:
        query.pop('tags')
    return "?"+query.urlencode(safe=',')
