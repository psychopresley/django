from django import template
from datetime import datetime

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


@register.simple_tag
def pct(value,decimal=2,normalized=True,absolute=False):
    """
    put some string here.
    """
    if normalized:
        k=100
    else:
        k=1

    if absolute:
        if value < 0:
            value *= -1

    return "%.{}f%%".format(decimal) % (value*k)


@register.simple_tag
def math(value,arg=1,op='sum',integer=True):
    """
    put some string here.
    """
    if op == 'sum':
        result = float(value) + float(arg)
    elif op == 'sub':
        result = float(value) - float(arg)
    elif op == 'mul':
        result = float(value) * float(arg)
    elif op == 'div':
        result = float(value)/float(arg)

    return format_integer(int(result),style='us') if integer else result
