# noinspection PyUnresolvedReferences
from django import template


register = template.Library()


@register.filter(name='downize')
def downize(value):
    return ('%s' % value).capitalize()
