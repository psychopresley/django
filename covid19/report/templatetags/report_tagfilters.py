from django import template
from datetime import datetime

register = template.Library()


@register.filter
def integer(value):
    """
    Returns value as an integer.
    """
    return int(value)

@register.filter
def mod(value):
    """
    Returns the absolut of value.
    """
    return abs(float(value))

@register.filter
def sum(value,arg):
    """
    Returns the result of value + arg.
    """
    return float(value) + float(arg)

@register.filter
def sub(value,arg):
    """
    Returns the result of value - arg.
    """
    return float(value) - float(arg)

@register.filter
def mul(value,arg):
    """
    Returns the result of value * arg.
    """
    return float(value)*float(arg)

@register.filter
def div(value,arg):
    """
    Returns the result of value/den.
    """
    return float(value)/float(arg)

@register.filter
def pct(value,normalized=True):
    """
    put some string here.
    """
    if normalized:
        k=100
    else:
        k=1

    return "%.2f%%" % (value*k)

@register.filter(name='style')
def format_integer(value,style=None):
    """
    put some string here.
    """
    if style=='us':
        return '{:,}'.format(value)
    else:
        return '{:,}'.format(value).replace(',','.')

@register.filter
def monthname(value):
    """
    put some string here.
    """
    date = datetime(int(value[:4]),int(value[-2:]),1)
    return date.strftime('%B/%y')

# ==============================================================================
#                                  CUSTOM TAGS
# ==============================================================================

@register.simple_tag
def get_value(value,idx=0,key="confirmed_month"):
    """
    put some string here.
    """
    return value[idx][key]
