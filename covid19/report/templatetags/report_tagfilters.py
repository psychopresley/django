from django import template

register = template.Library()

@register.filter(name='style')
def format_integer(value,style=None):
    """
    put some string here.
    """
    if style=='us':
        return '{:,}'.format(value)
    else:
        return '{:,}'.format(value).replace(',','.')

@register.filter(name='pct')
def percentage(value,precision=2):
    """
    put some string here.
    """
    return "%.{}f%%".format(precision) % (value*100)


@register.filter(name='pct_conv')
def percentage(value,precision=2):
    """
    put some string here.
    """
    return "%.{}f%%".format(precision) % (value)
