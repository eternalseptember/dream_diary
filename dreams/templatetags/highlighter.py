from django import template
import re
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(is_safe=True)
def highlighter(text, search):
    highlighted = re.sub('(?i)(%s)' % (re.escape(search)), '<span class="highlight">\\1</span>', text)
    return mark_safe(highlighted)
