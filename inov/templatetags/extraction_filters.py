from django import template
from ..models import ExtractionConfiguration

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Gets an item from a dictionary using a key.
    Usage: {{ mydict|get_item:key }}
    """
    return dictionary.get(key)

@register.filter
def get_type_label(type_code):
    """
    Returns the display label for a document type code
    """
    for code, label in ExtractionConfiguration.TypeDocument.choices:
        if code == type_code:
            return label
    return type_code