from django import template

register = template.Library()


@register.filter(name='if_null')
def if_null(value, arg):
    if not value:
        return arg
    else:
        return value


@register.filter(name='has_group')
def has_group(user, group_name):
    print(group_name)
    if group_name[0] == "-":
        return not user.groups.filter(name=group_name).exists()
    else:
        return user.groups.filter(name=group_name).exists()


@register.filter(name='max_len')
def max_len(word, length):
    if len(word) > length:
        return word[:length] + '..'
    else:
        return word
