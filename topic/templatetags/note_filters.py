from django import template
import re

register = template.Library()

@register.filter
def has_split_marker(note):
    if not note:
        return False
    return re.search(r'\r?\n---\r?\n', note) is not None