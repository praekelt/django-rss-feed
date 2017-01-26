from django import template

from rssfeed.models import Entry

register = template.Library()


@register.inclusion_tag(
    "rssfeed/inclusion_tags/entry_list.html", takes_context=True
)
def render_rssfeed(context):
    entries = Entry.objects.all()
    context["entry_list"] = entries[:10]
    return context
