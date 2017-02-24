from django import template

from rssfeed.models import Entry

register = template.Library()


@register.inclusion_tag("rssfeed/inclusion_tags/render_rssfeed.html")
def render_rssfeed(count=5):
    entries = Entry.objects.all()[:count]
    return {"entries": entries}
