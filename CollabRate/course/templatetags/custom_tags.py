from django import template

register = template.Library()

@register.filter
def times(number):
    """
    Returns a range from 0 to the given number.
    Usage in template:
        {% for i in some_number|times %}
    """
    try:
        return range(int(number))
    except (ValueError, TypeError):
        return []
