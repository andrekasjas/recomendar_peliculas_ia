from django import template

register = template.Library()

@register.filter(name='lengthrange')
def lengthrange(start, stop):
    return range(start, stop+1)

@register.filter
def custom_round(value, arg):
    try:
        arg = int(arg)
    except ValueError:
        arg = 0
    try:
        value = round(float(value), arg)
    except ValueError:
        pass
    return value
