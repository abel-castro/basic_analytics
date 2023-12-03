import urllib.parse

from django import template

register = template.Library()


@register.filter
def full_url_encode(value):
    return urllib.parse.quote(value, safe="")
